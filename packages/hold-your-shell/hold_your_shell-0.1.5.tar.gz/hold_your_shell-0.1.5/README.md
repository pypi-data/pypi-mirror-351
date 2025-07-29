# hold-your-shell

`hold-your-shell` is a command line program (TUI) that previews shell
scripts (or any shebang script) in a pager, and asks the user to
confirm execution.

This single file program is written for Python 3.x and only uses the
stdlib.

![image](https://github.com/user-attachments/assets/1219de6e-32b2-4dbe-8016-e836adf5d7e1)

## Install

Pip install:

```
pip install hold-your-shell
```

Manual install:

```
HY_BIN=~/.local/bin/hold-your-shell
mkdir -p $(dirname ${HY_BIN})

wget -O ${HY_BIN} https://raw.githubusercontent.com/EnigmaCurry/hold-your-shell/refs/heads/master/hold_your_shell/hold_your_shell.py

chmod +x ${HY_BIN}
```

## Usage

 * Pipe any script to the stdin of `hold-your-shell`.
 * The script will be previewed on the first tab shown: `Script Preview`.
 * Press TAB to cycle through the other tabs, including `Env Vars`.
 * Use the up, down, PgUp, PgDown, `j`, or `k` keys to scroll the
   text.
 * Use the left, right, `h`, or `l` keys to select the action and
   press `Enter` to confirm.
   * Choose `Yes` to run the script.
   * Choose `No` to cancel and quit (default).
   * Choose `Edit` to open the script in your preferred `$EDITOR`,
     allowing you to customize it before running it.
 
## Examples

### Read from stdin

```
echo "whoami" | hold-your-shell
```

```
echo -e '#!/bin/python\nprint("Hello from Python!")' | hold-your-shell
```


```
cat <<'EOF' | hold-your-shell
echo "What is your name?"
read NAME
echo "Hello $NAME"
EOF
```

```
curl https://get.docker.com/ | hold-your-shell
```

### Read from file

```
cat <<EOF > test.txt
#!/bin/env python
print("Hello from Python!")
EOF

hold-your-shell --consume test.txt
```

`--consume` will **delete** the input file immediately after it reads
it.

### Linger

```
echo whoami | hold-your-shell --linger
```

`--linger` will have the program remain running after completion of
the script until a key is pressed.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md)
