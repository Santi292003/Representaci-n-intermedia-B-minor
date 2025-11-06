; If/else anidado + comparaciones

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"x" = alloca i32
  store i32 7, i32* %"x"
  %"y" = alloca i32
  store i32 10, i32* %"y"
  %"r" = alloca i32
  store i32 0, i32* %"r"
  %"x.1" = load i32, i32* %"x"
  %"y.1" = load i32, i32* %"y"
  %"cmptmp" = icmp slt i32 %"x.1", %"y.1"
  br i1 %"cmptmp", label %"if.then", label %"if.else"
if.then:
  %"x.2" = load i32, i32* %"x"
  %"multmp" = mul i32 %"x.2", 2
  %"y.2" = load i32, i32* %"y"
  %"x.3" = load i32, i32* %"x"
  %"subtmp" = sub i32 %"x.3", 4
  %"subtmp.1" = sub i32 %"y.2", %"subtmp"
  %"cmptmp.1" = icmp eq i32 %"multmp", %"subtmp.1"
  br i1 %"cmptmp.1", label %"if.then.1", label %"if.else.1"
if.end:
  %"r.1" = load i32, i32* %"r"
  ret i32 %"r.1"
if.else:
  store i32 3, i32* %"r"
  br label %"if.end"
if.then.1:
  store i32 1, i32* %"r"
  br label %"if.end.1"
if.end.1:
  br label %"if.end"
if.else.1:
  store i32 2, i32* %"r"
  br label %"if.end.1"
}

