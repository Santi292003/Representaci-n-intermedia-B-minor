; While + if interno

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"n" = alloca i32
  store i32 8, i32* %"n"
  %"i" = alloca i32
  store i32 1, i32* %"i"
  %"acc" = alloca i32
  store i32 0, i32* %"acc"
  br label %"while.cond"
while.cond:
  %"i.1" = load i32, i32* %"i"
  %"n.1" = load i32, i32* %"n"
  %"cmptmp" = icmp sle i32 %"i.1", %"n.1"
  br i1 %"cmptmp", label %"while.body", label %"while.end"
while.body:
  %"i.2" = load i32, i32* %"i"
  %"modtmp" = srem i32 %"i.2", 2
  %"cmptmp.1" = icmp eq i32 %"modtmp", 0
  br i1 %"cmptmp.1", label %"if.then", label %"if.end"
while.end:
  %"acc.2" = load i32, i32* %"acc"
  ret i32 %"acc.2"
if.then:
  %"acc.1" = load i32, i32* %"acc"
  %"i.3" = load i32, i32* %"i"
  %"addtmp" = add i32 %"acc.1", %"i.3"
  store i32 %"addtmp", i32* %"acc"
  br label %"if.end"
if.end:
  %"i.4" = load i32, i32* %"i"
  %"addtmp.1" = add i32 %"i.4", 1
  store i32 %"addtmp.1", i32* %"i"
  br label %"while.cond"
}

