; for in range desazucarado

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"sum" = alloca i32
  store i32 0, i32* %"sum"
  %"i" = alloca i32
  store i32 1, i32* %"i"
  br label %"while.cond"
while.cond:
  %"i.1" = load i32, i32* %"i"
  %"cmptmp" = icmp slt i32 %"i.1", 6
  br i1 %"cmptmp", label %"while.body", label %"while.end"
while.body:
  %"sum.1" = load i32, i32* %"sum"
  %"i.2" = load i32, i32* %"i"
  %"addtmp" = add i32 %"sum.1", %"i.2"
  store i32 %"addtmp", i32* %"sum"
  %"i.3" = load i32, i32* %"i"
  %"addtmp.1" = add i32 %"i.3", 1
  store i32 %"addtmp.1", i32* %"i"
  br label %"while.cond"
while.end:
  %"sum.2" = load i32, i32* %"sum"
  ret i32 %"sum.2"
}

