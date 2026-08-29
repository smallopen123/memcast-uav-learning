"""Lesson 07: run the complete offline memory-conditioned forecast pipeline."""

import json

from memcast_uav.pipeline import run_demo


def main() -> None:
    result = run_demo(test_limit=10)
    print("课程07：端到端离线流程")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    print("解释重点：不要只看最终MSE，还要与constant-velocity基线比较。")

    # 实践：改变 memory limit、top-k 或 intent weight，并记录结果变化。


if __name__ == "__main__":
    main()

