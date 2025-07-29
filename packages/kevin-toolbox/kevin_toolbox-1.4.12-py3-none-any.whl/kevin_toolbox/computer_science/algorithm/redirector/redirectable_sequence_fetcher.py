import random
from kevin_toolbox.patches.for_logging import build_logger
from kevin_toolbox.patches.for_numpy.random import get_rng, set_rng_state, get_rng_state
from kevin_toolbox.computer_science.algorithm.cache_manager import Cache_Manager, Cache_Manager_wto_Strategy


def _randomly_idx_redirector(idx, seq_len, attempts, rng, *args):
    if idx == 0:
        return rng.randint(1, seq_len - 1)
    elif idx == seq_len - 1:
        return rng.randint(0, seq_len - 2)
    else:
        return rng.choice([rng.randint(0, idx - 1), rng.randint(idx + 1, seq_len - 1)], size=1,
                          p=[idx / (seq_len - 1), (seq_len - idx - 1) / (seq_len - 1)])[0]


idx_redirector_s = {
    "decrease": lambda idx, *args: idx - 1,
    "increase": lambda idx, *args: idx + 1,
    "randomly": _randomly_idx_redirector,
}

EMPTY = object()


def _round_idx(idx, st, ed):
    if idx < st or idx >= ed:
        idx = (idx - st) % (ed - st) + st
    assert st <= idx < ed
    return idx


class Redirectable_Sequence_Fetcher:
    """
        用于从给定 seq 中获取元素，通过跳转来处理获取失败的情况

        功能描述：
            1. 对于给定的索引 idx，若能通过 seq(idx) 成功获取，则直接返回获取的结果。
            2. 若不能成功获取，则会根据给定的规则修改索引（如idx-1）重新尝试获取，递归调用直至获取成功或者递归调用次数达到上限。
                2.a 若开启了跳转记忆功能，则会为获取失败的 idx 记录其最终重定向到的新的 idx，以及其获取失败的次数。
                    当失败次数达到上限后，则不再进行尝试并直接返回重新向后的新的 idx 的结果。
                    若在此过程中原来失败的 idx 又能再次获取成功，则将失败次数减1，直至归零并删除该记录。
            3. 若递归次数达到上限，则进行报错或者返回给定的默认值。
                3.a 若开启了跳转记忆功能，在重试过程中，一旦某次调用成功，记录原始索引与最终有效索引之间的映射关系。

        使用建议：
            - 数据读取或模型训练过程中，当某些外部因素导致部分索引数据获取失败时，自动进行索引跳转和重试，从而保证整个流程的鲁棒性和连续性。
    """

    def __init__(self, **kwargs):
        """
            参数：
                seq:                <callable> 元素获取器。
                                        要求能通过 seq(idx) 或者 seq[idx] 返回元素。
                value_checker:      <callable> 元素检查器。
                                        形如 func(v) ==> boolean 的函数，当返回 True 时表示成功获取。
                                        默认为 None，不对元素进行检查。
                seq_len:          <int> 序列长度。
                                        默认不指定，将尝试通过 len(seq) 获取。
                idx_redirector:     <str/callable> 对 idx 进行重定向的方式。
                                        形如 func(idx, seq_len, attempts, rng) ==> new_idx 的函数，
                                            其中 attempts 是已进行重定向的次数，rng是随机生成器。
                                        当设定为 str 时，则使用默认的函数。目前支持以下选项：
                                            - "decrease":       new_idx=idx-1
                                            - "increase":       new_idx=idx+1
                                            - "randomly":       随机跳转（默认）
                redirect_max_attempts:  <int> 进行重定向的次数上限。
                                        默认为 3。
                default_value:      <any> 重定向失败时返回的值。
                                        默认不指定，此时重定向失败后将引发报错。
                                        所谓重定向失败，就是在进行 redirect_max_attempts 次重定向后仍然无法成功获取值。
                memory:             <int/Cache_Manager> 跳转记忆器。
                                        当给定值为 int 时，将以该值为 upper_bound 构建 Cache_Manager，
                                            特别地，当设定为 -1 时，表示容量无上限。
                                        默认为 None，表示不使用记忆器。
                use_memory_after_failures:  <int> 在获取失败多少次后（failures计数+1大于该值后）将不再尝试获取而直接使用记忆。
                                        默认为 3。
                                        当设置为 None 时，表示从不使用记忆。
                memory_decay_rate:  <float> failures 计数衰减的速度。
                                        建议使用 0~1 之间的值。
                                        默认为 0.1，表示每直接使用一次记忆，则对 failures 计算减去 0.1
                logger:             <str/Logger> 用于记录每次发生的重定向行为。
                                        若为 dict，则需要包含 "target", "level", "formatter" 等键值对。
                                        若为 str，则会自动构建一个以该值为 target 的记录器。
                                            具体可以参见 for_logging.build_logger()
                                        默认为 None，表示不需要进行记录。
                seed:               <int>  随机种子
        """
        # 默认参数
        paras = {
            "seq": None,
            "value_checker": None,
            "idx_redirector": "randomly",
            "memory": None,
            #
            "seq_len": None,
            "redirect_max_attempts": 3,
            "default_value": EMPTY,
            "use_memory_after_failures": 3,
            "memory_decay_rate": 0.1,
            "logger": None,
            "seed": 114514
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        if paras["seq_len"] is None:
            assert hasattr(paras["seq"], "__len__"), "cannot infer the range of idx from seq"
            paras["seq_len"] = len(paras["seq"])
        assert paras["seq_len"] >= 0
        self.seq = paras["seq"]
        if hasattr(paras["seq"], "__getitem__"):
            self.seq = lambda idx: paras["seq"][idx]
        assert callable(self.seq)
        assert paras["value_checker"] is None or callable(paras["value_checker"])
        self.value_checker = paras["value_checker"]
        assert paras["redirect_max_attempts"] >= 0
        #
        self.idx_redirector = idx_redirector_s[paras[
            "idx_redirector"]] if paras["idx_redirector"] in idx_redirector_s else paras["idx_redirector"]
        assert callable(self.idx_redirector)
        #
        self.memory = paras["memory"]
        if paras["memory"] is not None:
            if isinstance(paras["memory"], int):
                self.memory = Cache_Manager(upper_bound=paras["memory"]
                                            ) if paras["memory"] > 0 else Cache_Manager_wto_Strategy()
            assert isinstance(self.memory, (Cache_Manager_wto_Strategy,))
        #
        self.logger = paras["logger"]
        if paras["logger"] is not None:
            if isinstance(paras["logger"], str):
                paras["logger"] = dict(target=paras["logger"])
            if isinstance(paras["logger"], dict):
                paras["logger"].setdefault("level", "INFO")
                self.logger = build_logger(name=f':Redirectable_Sequence_Fetcher:{id(self)}',
                                           handler_ls=[paras["logger"]], )
        #
        self.rng = get_rng(seed=paras["seed"], rng=None)

        self.paras = paras

    def fetch(self, idx):
        b_success = False
        error = None
        res = None
        try:
            res = self.seq(idx)
            b_success = True
        except Exception as e:
            error = e
        if self.value_checker is not None and b_success:
            b_success = self.value_checker(res)
            if not b_success:
                error = ValueError(f"value checker failed for idx={idx}")
        return res, b_success, error

    def redirectable_fetch(self, idx):
        attempts = 0
        new_idx = idx
        old_idx = idx

        # 尝试从 memory 中获取 new_idx
        b_use_memory = False
        if self.memory is not None and self.memory.has(key=idx):
            v_s = self.memory.get(key=idx)
            if "failures" in v_s and v_s["failures"] + 1 > self.paras["use_memory_after_failures"]:
                v_s["failures"] -= self.paras["memory_decay_rate"]
                attempts = self.paras["redirect_max_attempts"]
                new_idx = v_s["final"]
                b_use_memory = True
                if self.logger is not None:
                    self.logger.info(f"used memory for idx={idx}, jump to new_idx={new_idx}.")

        # 从 seq 中获取值
        res, b_success, error = None, False, None
        while attempts < self.paras["redirect_max_attempts"] + 1:
            res, b_success, error = self.fetch(new_idx)
            if b_success:
                if self.memory is not None and self.memory.has(key=new_idx):
                    v_s = self.memory.get(key=new_idx)
                    v_s["failures"] -= 1
                    if v_s["failures"] <= 1e-10:
                        self.memory.pop(key=new_idx)
                break
            old_idx = new_idx
            if self.paras["seq_len"] > 1:
                new_idx = self.idx_redirector(new_idx, self.paras["seq_len"], attempts, self.rng)
                new_idx = _round_idx(new_idx, st=0, ed=self.paras["seq_len"])
            #
            if self.memory is not None:
                v_s = self.memory.get(key=old_idx, b_add_if_not_found=True, default_factory=dict)
                v_s["next"] = new_idx
            #
            attempts += 1
            if self.logger is not None:
                self.logger.info(f"attempts {attempts}：")
                self.logger.warn(f"failed to fetch {old_idx}, because of {error}.")
                self.logger.info(f"redirected from {old_idx} to {new_idx}.")

        if not b_success:
            if self.logger is not None:
                self.logger.error(f"failed to fetch {idx} after {attempts} attempts, because of {error}.")
            if self.paras["default_value"] is EMPTY:
                raise error
            return self.paras["default_value"]
        else:
            if new_idx != idx and self.memory is not None:  # 经过了重定向
                v_s = self.memory.get(key=idx)
                v_s["final"] = new_idx
                if not b_use_memory:
                    v_s["failures"] = v_s.get("failures", 0) + 1
            return res

    def __call__(self, idx):
        if idx >= len(self) or idx < -len(self):
            raise IndexError("Index out of range")
        idx = _round_idx(idx, st=0, ed=len(self))
        return self.redirectable_fetch(idx)

    def __getitem__(self, idx):
        return self(idx)

    def __len__(self):
        return self.paras["seq_len"]

    def clear(self):
        if self.memory is not None:
            self.memory.clear()
        if self.logger is not None:
            self.logger.info("invoked clear()")

    # ---------------------- 用于保存和加载状态 ---------------------- #
    def load_state_dict(self, state_dict):
        """
            加载状态
        """
        self.clear()
        if self.logger is not None:
            self.logger.info("invoked load_state_dict()")
        if self.memory is not None:
            self.memory.load_state_dict(state_dict=state_dict["memory"])
        set_rng_state(state=state_dict["rng_state"], rng=self.rng)

    def state_dict(self, b_deepcopy=True):
        """
            获取状态
        """
        temp = {
            "memory": self.memory.state_dict(b_deepcopy=False) if self.memory is not None else None,
            "rng_state": get_rng_state(rng=self.rng),
        }
        if b_deepcopy:
            import kevin_toolbox.nested_dict_list as ndl
            temp = ndl.copy_(var=temp, b_deepcopy=True, b_keep_internal_references=True)
        return temp
