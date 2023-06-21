rv-ext-checker
==============

The rv-ext-checker utility can be used to determine what userspace
extensions a RISC-V platform supports.

Usage
-----

Clone and build https://github.com/riscv/riscv-opcodes.git:
```
 $ git clone https://github.com/riscv/riscv-opcodes.git
 $ cd riscv-opcodes
 $ make
```

There will now be a `instr_dict.yaml` in that repo.

Run gen.py:
```
gen.py -f /path/to/instr_dict.yaml -o output
```

You'll now end up with a bunch of C code in `output`. Build them:
```
for i in output/*.c; do clang --target=riscv64-linux-gnu ./$i -o $i.runme; done
```

Run the binaries on your RISC-V machine:
```
for i in *.runme; do echo Running $i; ./$i; done &> run.log
```

What does the machine support?
```
$ cat run.log | egrep 'ok$'|awk '{print $1}' | sort | uniq
a
c
c_d
c_zihintntl
d
f
i
m
zawrs
zba
zbb
zbc
zbe
zbp
zbs
zcmp
zcmt
zicbo
zifencei
zihintntl
zks
```

What does the machine NOT support?
```
b
d_zfa
d_zfh
f_zfa
h
q
q_zfa
q_zfh
v
v_aliases
zacas
zbc
zbe
zbf
zbm
zbp
zbpbo
zbr
zbt
zcb
zfbfmin
zfh
zfh_zfa
zicbo
zicond
zknd
zkne
zknh
zksed
zksh
zpn
zpsf
zvbb
zvbc
zvfbfmin
zvfbfwma
zvkg
zvkned
zvknha
zvksed
zvksh
```

Implementation
--------------

The python script simply extracts the instruction bit pattern, and
replaces the non-hardcoded parts with '1'.

Bugs
----

Some branching instructions will be reported as "sigill", due to the
"all-ones" filler.

Probably more. ;-)
