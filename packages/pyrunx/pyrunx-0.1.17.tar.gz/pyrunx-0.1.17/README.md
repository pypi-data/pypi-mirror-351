<div align="center">
  <h1>pythonrunner</h1>
</div>

**pythonrunner** is a program that allows you to run independent python scripts with a defined configuration.

<p align="center">
  <img src="https://img.shields.io/github/license/6C656C65/pythonrunner?style=for-the-badge">
  <img src="https://img.shields.io/github/issues/6C656C65/pythonrunner?style=for-the-badge">
  <img src="https://img.shields.io/github/issues-closed/6C656C65/pythonrunner?style=for-the-badge">
  <br>
  <img src="https://img.shields.io/github/forks/6C656C65/pythonrunner?style=for-the-badge">
  <img src="https://img.shields.io/github/stars/6C656C65/pythonrunner?style=for-the-badge">
  <img src="https://img.shields.io/github/commit-activity/w/6C656C65/pythonrunner?style=for-the-badge">
  <img src="https://img.shields.io/github/contributors/6C656C65/pythonrunner?style=for-the-badge">
  <br>
  <img src="https://img.shields.io/pypi/v/pyrunx?style=for-the-badge">
  <img src="https://img.shields.io/pypi/pyversions/pyrunx?style=for-the-badge">
</p>

---

## 📦 **Installation**

### Install from source

```bash
git clone https://github.com/6C656C65/pythonrunner.git
cd pythonrunner
pip install -r requirements.txt
```

### Install from package

```bash
pip install pyrunx
```

## ⚙️ **Configuration**

Pythonrunner requires a YAML configuration file. By default, it takes the `config.yml` or `config.yaml` file from the current directory.
Alternatively, you can use the `-c` or `--config` argument for the path to the file to use.
The file simply contains the variables that will be used in the extensions. Here is an example file:

```yml
crtsh:
  discord_token: "XXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  discord_prefix: "!"

dns:
  discord_token: "XXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  discord_prefix: "!"

rootme:
  discord_token: "XXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  discord_prefix: "!"
  api_key: XXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  users_uid:
    - uid: 000000
      pseudo: user1
    - uid: 111111
      pseudo: user2
...
```

## 🧩 **Extensions**

Pythonrunner will launch the python files located in the `extensions` folder. The python files can be in subfolders of this folder.
You can use the `-e` or `--extensions` argument to change the path of the folder to read.
Extensions are available on [this repository](https://github.com/6C656C65/pythonrunner-extensions).
Each of these extensions offers a configuration file. You can add the configurations to your file.

## 📚 **Documentation**

If you encounter any problems, or if you want to use the program in a particular way, I advise you to read the [documentation](https://github.com/6C656C65/pythonrunner/wiki).

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

Contributions are welcome and appreciated! If you'd like to improve this project, feel free to fork the repository and submit a pull request. Whether it's fixing bugs, adding new features, improving documentation, or suggesting enhancements, every bit helps. Please make sure to follow the coding standards and test your changes before submitting. Let's build something great together!

---
