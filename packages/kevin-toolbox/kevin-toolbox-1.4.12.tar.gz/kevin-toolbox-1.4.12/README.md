# kevin_toolbox

一个通用的工具代码包集合



环境要求

```shell
numpy>=1.19
pytorch>=1.2
```

安装方法：

```shell
pip install kevin-toolbox  --no-dependencies
```



[项目地址 Repo](https://github.com/cantbeblank96/kevin_toolbox)

[使用指南 User_Guide](./notes/User_Guide.md)

[免责声明 Disclaimer](./notes/Disclaimer.md)

[版本更新记录](./notes/Release_Record.md)：

- v 1.4.12 （2025-05-28）【bug fix】【new feature】
  - computer_science.algorithm.statistician
    - 【new feature】add Maximum_Accumulator，用于计算最大值的累积器。
    - 【new feature】add Minimum_Accumulator，用于计算最小值的累积器。

  - patches.for_numpy.linalg
    - 【bug fix】fix bug in softmax，修复了在 b_use_log_over_x=True 时 temperature 设为 None 导致计算失败的问题。


