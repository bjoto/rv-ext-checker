#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2023 by Rivos Inc.
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import sys
import yaml
import jinja2
import re
import os

# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))

def parse_input_options():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file", "-f", type=str, required=True, help="input file", metavar="<input file>"
    )
    parser.add_argument(
        "--output", "-o", type=str, required=True, help="output file",
        metavar="<output file>"
    )

    args = parser.parse_args()
    return args

def main():
    args = parse_input_options()
    input_file = open(args.file, "r")

    y = yaml.safe_load(input_file)

    top =  """
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>

static const char *curr;

static void sighandler(int sig)
{
        if (sig == SIGILL) {
                printf("%s sigill", curr);
                exit(1);
        }

        printf("%s sig:%d ok\\n", curr, sig);
        exit(0);
}

int main()
{
        if (signal(SIGILL, sighandler) == SIG_ERR)
                exit(2);
        if (signal(SIGSEGV, sighandler) == SIG_ERR)
                exit(2);
        if (signal(SIGBUS, sighandler) == SIG_ERR)
                exit(2);
    """

    cprog = jinja2.Template(
    """
        curr = "{{ ext }} {{ insn }}";
        asm volatile (
    {% if comp == "c" %}
                ".2byte {{ full_insn }}\\n\\t"
    {% else %}
                ".4byte {{ full_insn }}\\n\\t"
    {% endif %}
                : : : "memory");

        printf("%s ok\\n", curr);

    """)

    bottom = """
    }
    """

    with open(f"{args.output}", "w") as f:
        f.write(top)
        for d in y:
            # skip rv32 and system insns
            if "rv32_" in y[d]['extension'][0] or "rv_s" in y[d]['extension'][0] \
               or "rv_zicsr" in y[d]['extension'][0]:
                continue

            ext = y[d]['extension'][0] # XXX
            ext = re.sub(r'^rv64_', '', ext)
            ext = re.sub(r'^rv_', '', ext)
            insn = d.replace("_", ".")

            enc = y[d]['encoding']
            comp = "X"
            if re.match('^zc', ext) or re.match('^c', ext):
                enc = enc[16:]
                comp = "c"

            enc = enc.replace('-', '1')

            f.write(cprog.render(ext=ext, insn=insn, comp=comp, full_insn=hex(int(enc, 2))))
        f.write(bottom)
        f.close()

    print("Now build with:")
    print(f"$ clang-18 --target=riscv64-linux-gnu {args.output} -o {args.output}.runme")

if __name__ == "__main__":
    main()
