# CeFiM
We are Insper's Finance and Macroeconomics Unit. This repository holds code 
and data used in our studies.

# Installation
```commandline
pip install cefim
```

Updates to this package are very frequent. Always make sure you are using the latest version.
```commandline
pip install cefim --upgrade
```

# Data Feeder
All of our data can be retrieved through the `CefinData` class. The available methods are:
- `bcb_focus()`: Survey of professional forecasts of the Brazialian Central Bank. Source is from the [Brazilian Central Bank website](https://www3.bcb.gov.br/expectativas2/#/consultas). We have cleaned and strucured the original data.
- `titulos_publicos()`: Brazilian Public Bonds secondary market. Source is from the [Brazilian Central Bank website](https://www4.bcb.gov.br/pom/demab/negociacoes/apresentacao.asp?frame=1). We have cleaned and strucured the original data.
  - `ntnb()`: a subset of `titulos_publicos()` with only the inflation linked bonds.
