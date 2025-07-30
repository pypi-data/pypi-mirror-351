# Python env3
https://github.com/hailiang-wang/python-env3

.env file reader.

```
pip install -U env3
```

1) first, try to read env from parameter
2) second, try to read env from cwd dir
3) third, try to read env from ~/.env


```
import env3

ENV = env3.read_env() # env3.read_env(ENV_FILE_PATH), ENV_FILE_PATH is optional
print(ENV)
print(ENV.get("DEEKSEEK_MODEL"))
print(ENV.get("DEEKSEEK_MODEL2", "foo"))
env3.print_env(ENV)
```

# License

[LICENSE](./LICENSE)