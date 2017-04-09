# Embedded Brain Fuck

The Embedded Brain Fuck (EBF) language is an extension of the classic Brain Fuck language. It adds
some extra instructions for easier computation on an embedded system. The provided compiler
generates portable C code which may then be compiled using a system specific C compiler. The
generated code also includes user implementable hooks, which may be used to setup an embedded system
or provide special functions that cannot be implemented in EBF (such as interrupt handling or
complex device drivers).

For more information on the language see the [documentation](doc/mainpage.md).
