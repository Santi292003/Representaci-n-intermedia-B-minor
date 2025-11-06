; Aritmética + unario (-)

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca i32
  store i32 10, i32* %"a"
  %"b" = alloca i32
  store i32 3, i32* %"b"
  %"c" = alloca i32
  %"a.1" = load i32, i32* %"a"
  %"b.1" = load i32, i32* %"b"
  %"multmp" = mul i32 %"a.1", %"b.1"
  %"a.2" = load i32, i32* %"a"
  %"b.2" = load i32, i32* %"b"
  %"divtmp" = sdiv i32 %"a.2", %"b.2"
  %"subtmp" = sub i32 %"multmp", %"divtmp"
  %"b.3" = load i32, i32* %"b"
  %"negtmp" = sub i32 0, %"b.3"
  %"addtmp" = add i32 %"subtmp", %"negtmp"
  store i32 %"addtmp", i32* %"c"
  %"c.1" = load i32, i32* %"c"
  ret i32 %"c.1"
}

