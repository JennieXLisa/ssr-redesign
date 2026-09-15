/* Trusted, harness-authored capability probe. Never compile reviewed source. */
#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1], "payload")) return 77;
    if (argc != 3) return 2;
    const char *mode = argv[1], *value = argv[2];
    int result = -1, saved = 0, fd = -1;
    if (!strcmp(mode, "read")) {
        fd = open(value, O_RDONLY); result = fd;
    } else if (!strcmp(mode, "write")) {
        fd = open(value, O_WRONLY | O_CREAT | O_TRUNC, 0600); result = fd;
    } else if (!strcmp(mode, "directory")) {
        DIR *dir = opendir(value); saved = errno; result = dir ? 0 : -1;
        if (dir) closedir(dir);
    } else if (!strcmp(mode, "exec")) {
        execl(value, value, "payload", (char *)NULL); result = -1;
    } else if (!strcmp(mode, "map_exec")) {
        fd = open(value, O_RDONLY);
        if (fd >= 0) {
            void *ptr = mmap(NULL, 1, PROT_READ | PROT_EXEC, MAP_PRIVATE, fd, 0);
            result = ptr == MAP_FAILED ? -1 : 0; saved = errno;
            if (ptr != MAP_FAILED) munmap(ptr, 1);
        }
    } else if (!strcmp(mode, "child_read")) {
        pid_t child = fork();
        if (child == -1) return 3;
        if (!child) {
            fd = open(value, O_RDONLY); saved = errno;
            if (fd >= 0) close(fd);
            _exit(fd < 0 && (saved == EACCES || saved == EPERM) ? 0 : 1);
        }
        int status;
        if (waitpid(child, &status, 0) < 0) return 4;
        result = WIFEXITED(status) && WEXITSTATUS(status) == 0 ? -1 : 0;
        saved = result < 0 ? EACCES : 0;
    } else if (!strcmp(mode, "unix")) {
        struct sockaddr_un addr = {0}; addr.sun_family = AF_UNIX;
        if (strlen(value) >= sizeof(addr.sun_path)) return 5;
        strcpy(addr.sun_path, value);
        fd = socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd >= 0) result = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    } else if (!strcmp(mode, "tcp4") || !strcmp(mode, "udp4")) {
        struct sockaddr_in addr = {0}; addr.sin_family = AF_INET;
        addr.sin_port = htons((unsigned short)atoi(value));
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
        int udp = !strcmp(mode, "udp4");
        fd = socket(AF_INET, udp ? SOCK_DGRAM : SOCK_STREAM, 0);
        if (fd >= 0) result = udp ? (int)sendto(fd, "x", 1, 0, (struct sockaddr *)&addr, sizeof(addr))
                                 : connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    } else if (!strcmp(mode, "tcp6")) {
        struct sockaddr_in6 addr = {0}; addr.sin6_family = AF_INET6;
        addr.sin6_port = htons((unsigned short)atoi(value));
        inet_pton(AF_INET6, "::1", &addr.sin6_addr);
        fd = socket(AF_INET6, SOCK_STREAM, 0);
        if (fd >= 0) result = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    } else return 6;
    if (!saved) saved = errno;
    if (fd >= 0) close(fd);
    printf("{\"allowed\":%s,\"errno\":%d}\n", result >= 0 ? "true" : "false", result >= 0 ? 0 : saved);
    return 0;
}
