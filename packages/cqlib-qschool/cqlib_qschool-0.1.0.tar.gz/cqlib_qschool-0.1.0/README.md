# 天衍量子计算校验平台

## 安装

目前支持 Python 3.10+ 版本 ，推荐使用 pip 安装:

```bash
pip install cqlib-qschool
```

## 示例

登录 [天衍量子计算校验平台](https://qschool.zdxlz.com/lab/dashboard) ，获取链接密钥。并替换下面的 `<LOGIN-KEY>`。

```python
from cqlib import Circuit
from cqlib.mapping import transpile_qcis
from qschool import QSchoolPlatform

circuit = Circuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

pf = QSchoolPlatform(login_key="<LOGIN-KEY>", machine_name='tianyan504')
new_circuit, _, _, _ = transpile_qcis(circuit.qcis, pf)

query_id = pf.submit_experiment(new_circuit.qcis, num_shots=1000)
data = pf.query_experiment(query_id, readout_calibration=True)
print(data[0])
```

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
