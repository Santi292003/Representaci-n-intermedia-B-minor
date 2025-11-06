; Comparaciones combinadas

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca i32
  store i32 5, i32* %"a"
  %"b" = alloca i32
  store i32 5, i32* %"b"
  %"c" = alloca i32
  store i32 7, i32* %"c"
  %"r" = alloca i32
  store i32 0, i32* %"r"
  %"a.1" = load i32, i32* %"a"
  %"b.1" = load i32, i32* %"b"
  %"cmptmp" = icmp eq i32 %"a.1", %"b.1"
  %"c.1" = load i32, i32* %"c"
  %"b.2" = load i32, i32* %"b"
  %"cmptmp.1" = icmp ne i32 %"c.1", %"b.2"
  %"a.2" = load i32, i32* %"a"
  %"b.3" = load i32, i32* %"b"
  %"cmptmp.2" = icmp eq i32 %"a.2", %"b.3"
  br i1 %"cmptmp.2", label %"and.rhs", label %"and.end"
and.rhs:
  %"c.2" = load i32, i32* %"c"
  %"b.4" = load i32, i32* %"b"
  %"cmptmp.3" = icmp ne i32 %"c.2", %"b.4"
  br label %"and.end"
and.end:
  %"andtmp" = phi  i1 [0, %"entry"], [%"cmptmp.3", %"and.rhs"]
  %"c.3" = load i32, i32* %"c"
  %"a.3" = load i32, i32* %"a"
  %"cmptmp.4" = icmp sge i32 %"c.3", %"a.3"
  %"a.4" = load i32, i32* %"a"
  %"b.5" = load i32, i32* %"b"
  %"cmptmp.5" = icmp eq i32 %"a.4", %"b.5"
  %"c.4" = load i32, i32* %"c"
  %"b.6" = load i32, i32* %"b"
  %"cmptmp.6" = icmp ne i32 %"c.4", %"b.6"
  %"a.5" = load i32, i32* %"a"
  %"b.7" = load i32, i32* %"b"
  %"cmptmp.7" = icmp eq i32 %"a.5", %"b.7"
  br i1 %"cmptmp.7", label %"and.rhs.1", label %"and.end.1"
and.rhs.1:
  %"c.5" = load i32, i32* %"c"
  %"b.8" = load i32, i32* %"b"
  %"cmptmp.8" = icmp ne i32 %"c.5", %"b.8"
  br label %"and.end.1"
and.end.1:
  %"andtmp.1" = phi  i1 [0, %"and.end"], [%"cmptmp.8", %"and.rhs.1"]
  br i1 %"andtmp.1", label %"and.rhs.2", label %"and.end.2"
and.rhs.2:
  %"c.6" = load i32, i32* %"c"
  %"a.6" = load i32, i32* %"a"
  %"cmptmp.9" = icmp sge i32 %"c.6", %"a.6"
  br label %"and.end.2"
and.end.2:
  %"andtmp.2" = phi  i1 [0, %"and.end.1"], [%"cmptmp.9", %"and.rhs.2"]
  %"a.7" = load i32, i32* %"a"
  %"b.9" = load i32, i32* %"b"
  %"cmptmp.10" = icmp sle i32 %"a.7", %"b.9"
  %"a.8" = load i32, i32* %"a"
  %"b.10" = load i32, i32* %"b"
  %"cmptmp.11" = icmp eq i32 %"a.8", %"b.10"
  %"c.7" = load i32, i32* %"c"
  %"b.11" = load i32, i32* %"b"
  %"cmptmp.12" = icmp ne i32 %"c.7", %"b.11"
  %"a.9" = load i32, i32* %"a"
  %"b.12" = load i32, i32* %"b"
  %"cmptmp.13" = icmp eq i32 %"a.9", %"b.12"
  br i1 %"cmptmp.13", label %"and.rhs.3", label %"and.end.3"
and.rhs.3:
  %"c.8" = load i32, i32* %"c"
  %"b.13" = load i32, i32* %"b"
  %"cmptmp.14" = icmp ne i32 %"c.8", %"b.13"
  br label %"and.end.3"
and.end.3:
  %"andtmp.3" = phi  i1 [0, %"and.end.2"], [%"cmptmp.14", %"and.rhs.3"]
  %"c.9" = load i32, i32* %"c"
  %"a.10" = load i32, i32* %"a"
  %"cmptmp.15" = icmp sge i32 %"c.9", %"a.10"
  %"a.11" = load i32, i32* %"a"
  %"b.14" = load i32, i32* %"b"
  %"cmptmp.16" = icmp eq i32 %"a.11", %"b.14"
  %"c.10" = load i32, i32* %"c"
  %"b.15" = load i32, i32* %"b"
  %"cmptmp.17" = icmp ne i32 %"c.10", %"b.15"
  %"a.12" = load i32, i32* %"a"
  %"b.16" = load i32, i32* %"b"
  %"cmptmp.18" = icmp eq i32 %"a.12", %"b.16"
  br i1 %"cmptmp.18", label %"and.rhs.4", label %"and.end.4"
and.rhs.4:
  %"c.11" = load i32, i32* %"c"
  %"b.17" = load i32, i32* %"b"
  %"cmptmp.19" = icmp ne i32 %"c.11", %"b.17"
  br label %"and.end.4"
and.end.4:
  %"andtmp.4" = phi  i1 [0, %"and.end.3"], [%"cmptmp.19", %"and.rhs.4"]
  br i1 %"andtmp.4", label %"and.rhs.5", label %"and.end.5"
and.rhs.5:
  %"c.12" = load i32, i32* %"c"
  %"a.13" = load i32, i32* %"a"
  %"cmptmp.20" = icmp sge i32 %"c.12", %"a.13"
  br label %"and.end.5"
and.end.5:
  %"andtmp.5" = phi  i1 [0, %"and.end.4"], [%"cmptmp.20", %"and.rhs.5"]
  br i1 %"andtmp.5", label %"and.rhs.6", label %"and.end.6"
and.rhs.6:
  %"a.14" = load i32, i32* %"a"
  %"b.18" = load i32, i32* %"b"
  %"cmptmp.21" = icmp sle i32 %"a.14", %"b.18"
  br label %"and.end.6"
and.end.6:
  %"andtmp.6" = phi  i1 [0, %"and.end.5"], [%"cmptmp.21", %"and.rhs.6"]
  br i1 %"andtmp.6", label %"if.then", label %"if.end"
if.then:
  store i32 10, i32* %"r"
  br label %"if.end"
if.end:
  %"r.1" = load i32, i32* %"r"
  ret i32 %"r.1"
}

