#!/usr/bin/env python3
import sys
import subprocess

try:
    import gdb

except:
    from shutil import which
    from os.path import basename

    args = sys.argv
    selfName = args.pop(0)

    if not selfName.endswith(".py"):
        print("'%s' needs to end with '.py'" % basename(selfName))
        exit(1)

    if not which("gdb"):
        print("'gdb' binary not found")
        exit(1)

    print("Starting gdb - please wait...")
    subprocess.call(["gdb", "--silent", "--command", selfName, "--args"] + args)
    exit(0)


def printq6string(val):
    d = val['d']
    data = d['ptr'].reinterpret_cast(gdb.lookup_type('char').pointer())
    data_len = d['size'] * gdb.lookup_type('unsigned short').sizeof
    return data.string('utf-16', 'replace', data_len)


def breakpointHandler(event):
    frame = gdb.newest_frame()

    if frame.name() == "QQmlPropertyBinding::createBindingLoopErrorDescription" or \
       frame.name() == "QQmlAbstractBinding::printBindingLoopError":

        print("===== Binding loop detected =====")
        print("\nBacktrace:")

        i = 0
        while True:
            frame = frame.older()

            if frame == None or not frame.is_valid():
                break

            if frame.name() == "QQmlBinding::update":
                currentBinding = frame.read_var("this")
                eval_string = "(*(QQmlBinding*)(%s)).expressionIdentifier()" % str(currentBinding)
                identifier = printq6string(gdb.parse_and_eval(eval_string))
                print("#" + str(i) + " - " + identifier)
                i+=1

        print()

        gdb.execute("continue")


def main():
    gdb.events.stop.connect(breakpointHandler)

    bp1 = gdb.Breakpoint("QQmlPropertyBinding::createBindingLoopErrorDescription")
    bp2 = gdb.Breakpoint("QQmlAbstractBinding::printBindingLoopError")

    gdb.execute("run")


if __name__ == "__main__":
    main()

