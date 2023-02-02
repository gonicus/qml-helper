# Traces for binding loops

Sometimes you manage to create *binding loops* in QML. That basically means
that there's a change to a property *x*, which uses QML bindings in its
calculation, loops back to itself after it has been modified.

While many of them are obvious and easy to fix, it can become tricky to
understand the cause if there are various nested components involved. You'll
just get some

```shell
8:45:32.168 ?foo?|qt_message_output|QDebug::~QDebug \
  qrc:/de/gonicus/ui/components/controls/Spinner.qml:199:5: \
  QML TextField: Binding loop detected for property "text"
```

and you've no idea what it comes from after some digging.

For me, this always ended up in the debugger, looking at the backtrace, and
trying to understand what's going on manually.

## Automation with gdb

Doing it a couple of times in the past, I stumbled upon a 2016 blog entry of 
[David Edmundson](git@github.com:gonicus/qml-helper.git), who did a small
python script to automate the tracing for Qt 5. Based on his work, I've adapted
it to work with Qt 6.

### Preconditions

To make use of the script, you need Qt 6 and `gdb` packages installed.

### Usage

Just run `loop-tracker.py path/to/your/binary`. This will fire up **gdb** and
start your app. Slowly. When it traps into a binding loop, it unwinds the stack
and tries to find places where the update happens. It then prints the QML
file / line number, and continues.

```
$ ./loop-tracker.py ~/Qt/6.5.0/gcc_64/bin/qmlscene test.qml 
Starting gdb - please wait...
[...]
Thread 1 "qmlscene" hit Breakpoint 1, QQmlPropertyBinding::createBindingLoopErrorDescription (this=0x43bb20) at /home/qt/work/qt/qtdeclarative/src/qml/qml/qqmlpropertybinding.cpp:265
265	/home/qt/work/qt/qtdeclarative/src/qml/qml/qqmlpropertybinding.cpp: No such file or directory.
===== Binding loop detected =====

Backtrace:
#0 - file:///var/home/prcs1076/Projekte/qml-helper/binding-loops/test.qml:6:9

file:///var/home/prcs1076/Projekte/qml-helper/binding-loops/test.qml:4:5: QML Rectangle: Binding loop detected for property "width"
[...]
```

That's not perfect, but helped to find some of the more hidden loops here.