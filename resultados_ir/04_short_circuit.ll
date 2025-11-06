; Short-circuit lógico

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca i32
  store i32 0, i32* %"a"
  %"b" = alloca i32
  store i32 5, i32* %"b"
  %"x" = alloca i32
  store i32 0, i32* %"x"
  %"a.1" = load i32, i32* %"a"
  %"cmptmp" = icmp eq i32 %"a.1", 0
  %"b.1" = load i32, i32* %"b"
  %"a.2" = load i32, i32* %"a"
  %"divtmp" = sdiv i32 %"b.1", %"a.2"
  %"cmptmp.1" = icmp sgt i32 %"divtmp", 0
  %"a.3" = load i32, i32* %"a"
  %"cmptmp.2" = icmp eq i32 %"a.3", 0
  br i1 %"cmptmp.2", label %"or.end", label %"or.rhs"
or.rhs:
  %"b.2" = load i32, i32* %"b"
  %"a.4" = load i32, i32* %"a"
  %"divtmp.1" = sdiv i32 %"b.2", %"a.4"
  %"cmptmp.3" = icmp sgt i32 %"divtmp.1", 0
  br label %"or.end"
or.end:
  %"ortmp" = phi  i1 [1, %"entry"], [%"cmptmp.3", %"or.rhs"]
  br i1 %"ortmp", label %"if.then", label %"if.end"
if.then:
  %"x.1" = load i32, i32* %"x"
  %"addtmp" = add i32 %"x.1", 1
  store i32 %"addtmp", i32* %"x"
  br label %"if.end"
if.end:
  %"a.5" = load i32, i32* %"a"
  %"cmptmp.4" = icmp ne i32 %"a.5", 0
  %"b.3" = load i32, i32* %"b"
  %"a.6" = load i32, i32* %"a"
  %"divtmp.2" = sdiv i32 %"b.3", %"a.6"
  %"cmptmp.5" = icmp sgt i32 %"divtmp.2", 0
  %"a.7" = load i32, i32* %"a"
  %"cmptmp.6" = icmp ne i32 %"a.7", 0
  br i1 %"cmptmp.6", label %"and.rhs", label %"and.end"
and.rhs:
  %"b.4" = load i32, i32* %"b"
  %"a.8" = load i32, i32* %"a"
  %"divtmp.3" = sdiv i32 %"b.4", %"a.8"
  %"cmptmp.7" = icmp sgt i32 %"divtmp.3", 0
  br label %"and.end"
and.end:
  %"andtmp" = phi  i1 [0, %"if.end"], [%"cmptmp.7", %"and.rhs"]
  br i1 %"andtmp", label %"if.then.1", label %"if.end.1"
if.then.1:
  %"x.2" = load i32, i32* %"x"
  %"addtmp.1" = add i32 %"x.2", 10
  store i32 %"addtmp.1", i32* %"x"
  br label %"if.end.1"
if.end.1:
  %"x.3" = load i32, i32* %"x"
  ret i32 %"x.3"
}

