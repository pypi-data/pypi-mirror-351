import json
from dataclasses import dataclass, field, fields

import torch
import triton
import triton.language as tl

from .fwd_kernels import load_toeplitz


def setup_inputs(bs, seqlen, dg, g, filter_size, dtype, requires_grad=True):
    device = "cuda"
    x = torch.randn(bs, seqlen, g, dg, device=device, dtype=dtype, requires_grad=requires_grad)
    B = torch.randn(bs, seqlen, g, dg, device=device, dtype=dtype, requires_grad=requires_grad)
    C = torch.randn(bs, seqlen, g, dg, device=device, dtype=dtype, requires_grad=requires_grad)
    h = torch.randn(g * filter_size, device=device, dtype=dtype, requires_grad=requires_grad).reshape(g, 1, filter_size)
    return x, B, C, h


def print_diff(expected: torch.Tensor, actual: torch.Tensor, msg=""):
    actual = actual.reshape_as(expected)
    if msg == "":
        print(f"\nDiff: {(expected - actual).abs().max():.6f}", end="\n")
    else:
        print(f"{msg}: {(expected - actual).abs().max():.6f}", end="\n")


def get_test_diffs(expected, actual, rtol=1e-3, atol=1e-3, verbose=False):
    max_diff = (expected - actual).abs().max()
    diff = (expected - actual).abs()
    idx = diff.argmax()
    actual_at_max_diff = actual.reshape(-1)[idx]
    expected_at_max_diff = expected.reshape(-1)[idx]

    rtol_diff = actual_at_max_diff.abs() * rtol
    rel_diff = atol + rtol_diff

    if verbose:
        print(f"max_diff = {max_diff}")

        print(f"Expected at max diff = {actual_at_max_diff}, Actual = {expected_at_max_diff}")

        print(f"rel_diff = {rel_diff} = {atol} + {rtol_diff}")

    print(f"allclose = {torch.allclose(expected, actual, rtol=rtol, atol=atol)}")

    return max_diff, rel_diff


def print_device_props():
    from triton.runtime import driver

    device = torch.cuda.current_device()
    properties = driver.active.utils.get_device_properties(device)
    NUM_SM = properties["multiprocessor_count"]
    NUM_REGS = properties["max_num_regs"]
    SIZE_SMEM = properties["max_shared_mem"]
    WARP_SIZE = properties["warpSize"]
    target = triton.runtime.driver.active.get_current_target()
    print(f"{target=} {NUM_SM=} {NUM_REGS=} {SIZE_SMEM=} {WARP_SIZE=}")


@triton.jit
def toeplitz_load_kernel(
    h_ptr,
    group_num,
    T_ptr,
    FILTER_LEN: tl.constexpr,
    CHUNK_SIZE: tl.constexpr,
    SINGLE_GROUP: tl.constexpr,
):
    T = load_toeplitz(h_ptr, FILTER_LEN, CHUNK_SIZE, SINGLE_GROUP=SINGLE_GROUP, group_num=group_num)
    store_idx = tl.arange(0, CHUNK_SIZE)
    row_idx = store_idx[:, None] * CHUNK_SIZE
    col_idx = store_idx[None, :]
    tl.store(T_ptr + row_idx + col_idx, T)


@dataclass
class TestResult:
    name: str
    is_interpreter: bool
    schedule: str
    bs: int
    seqlen: int
    d: int
    g: int
    dtype: torch.dtype
    USE_TMA: bool
    FILTER_LEN: int
    CHUNK_SIZE: int
    BLOCK_D: int
    ATOL: float
    RTOL: float

    @classmethod
    def get_header(cls):
        return ",".join(f.name for f in fields(cls))

    def _exclude_from_str(self):
        tensor_fields = [f.name for f in fields(self) if isinstance(getattr(self, f.name), torch.Tensor)]
        return tensor_fields

    def __str__(self):
        props = {k: v for k, v in self.__dict__.items() if k not in self._exclude_from_str()}
        # Add for easy filtering from rest of pytest output
        props.update({self._SENTINEL: self.name})
        return json.dumps(props)

    def diffs(self):
        raise NotImplementedError

    def __post_init__(self):
        self.dtype = str(self.dtype).split(".")[-1]
        self._SENTINEL = "__DEBUG__"

    @property
    def passed(self):
        passes = self._passes()
        return all(passes)


def get_diff(expected: torch.Tensor, actual: torch.Tensor, reduction="max"):
    diff = (expected - actual).abs().max() if reduction == "max" else (expected - actual).abs().mean()
    return diff.cpu().item()


def set_chunk_size(seqlen, hl):
    if seqlen > 1024:
        CHUNK_SIZE = 128
    else:
        CHUNK_SIZE = max(hl, 32)

    return CHUNK_SIZE


@dataclass
class FwdTestResult(TestResult):
    return_y2: bool
    return_toeplitz: bool
    return_bx_lag: bool
    y_ref: torch.Tensor
    y: torch.Tensor
    version: str
    T_ref: torch.Tensor = None
    T_hat_ref: torch.Tensor = None
    y2_ref: torch.Tensor = None
    T: torch.Tensor = None
    T_hat: torch.Tensor = None
    y2: torch.Tensor = None
    y_diff: float = field(init=False)
    T_diff: float = field(init=False)
    T_hat_diff: float = field(init=False)
    y2_diff: float = field(init=False)
    y_passed: bool = field(init=False)
    T_passed: bool = field(init=False)
    T_hat_passed: bool = field(init=False)
    y2_passed: bool = field(init=False)

    def _exclude_from_str(self):
        return super()._exclude_from_str() + [
            "y2",
            "T",
            "T_hat",
            "y2_ref",
            "T_ref",
            "T_hat_ref",
        ]

    def diffs(self):
        y_diff = get_diff(self.y_ref, self.y)
        T_diff = get_diff(self.T_ref, self.T) if self.T_ref is not None else None
        T_hat_diff = get_diff(self.T_hat_ref, self.T_hat) if self.T_hat_ref is not None else None
        y2_diff = get_diff(self.y2_ref, self.y2) if self.y2_ref is not None else None
        return y_diff, T_diff, T_hat_diff, y2_diff

    def _passes(self):
        y_passed = torch.allclose(self.y_ref, self.y, atol=self.ATOL, rtol=self.RTOL)
        T_passed = (
            torch.allclose(self.T_ref, self.T, atol=self.ATOL, rtol=self.RTOL) if self.T_ref is not None else True
        )
        T_hat_passed = (
            torch.allclose(self.T_hat_ref, self.T_hat, atol=self.ATOL, rtol=self.RTOL)
            if self.T_hat_ref is not None
            else True
        )
        y2_passed = (
            torch.allclose(self.y2_ref, self.y2, atol=self.ATOL, rtol=self.RTOL) if self.y2_ref is not None else True
        )
        return y_passed, T_passed, T_hat_passed, y2_passed

    def __post_init__(self):
        super().__post_init__()
        self.y_diff, self.T_diff, self.T_hat_diff, self.y2_diff = self.diffs()
        self.y_passed, self.T_passed, self.T_hat_passed, self.y2_passed = self._passes()


@dataclass
class BwdTestResult(TestResult):
    version: str
    load_toeplitz: bool
    load_bx_lag: bool
    dx_ref: torch.Tensor
    dx: torch.Tensor
    dB_ref: torch.Tensor
    dB: torch.Tensor
    dC_ref: torch.Tensor
    dC: torch.Tensor
    dh_ref: torch.Tensor
    dh: torch.Tensor
    ATOL_dh: float = None
    RTOL_dh: float = None
    dx_diff: float = field(init=False)
    dB_diff: float = field(init=False)
    dC_diff: float = field(init=False)
    dh_diff: float = field(init=False)
    dx_passed: bool = field(init=False)
    dB_passed: bool = field(init=False)
    dC_passed: bool = field(init=False)
    dh_passed: bool = field(init=False)

    def diffs(self):
        return (
            get_diff(self.dx_ref, self.dx),
            get_diff(self.dB_ref, self.dB),
            get_diff(self.dC_ref, self.dC),
            get_diff(self.dh_ref, self.dh),
        )

    def _passes(self):
        dx_passed = torch.allclose(self.dx_ref, self.dx, atol=self.ATOL, rtol=self.RTOL)
        dB_passed = torch.allclose(self.dB_ref, self.dB, atol=self.ATOL, rtol=self.RTOL)
        dC_passed = torch.allclose(self.dC_ref, self.dC, atol=self.ATOL, rtol=self.RTOL)
        dh_passed = torch.allclose(self.dh_ref, self.dh, atol=self.ATOL_dh, rtol=self.RTOL_dh)
        return dx_passed, dB_passed, dC_passed, dh_passed

    def __post_init__(self):
        super().__post_init__()
        if self.ATOL_dh is None:
            self.ATOL_dh = self.ATOL
        if self.RTOL_dh is None:
            self.RTOL_dh = self.RTOL

        self.dx_diff, self.dB_diff, self.dC_diff, self.dh_diff = self.diffs()
        self.dx_passed, self.dB_passed, self.dC_passed, self.dh_passed = self._passes()
