#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>

__attribute__((no_instrument_function))
static void print_function(void *addr)
{
    Dl_info info;

    if (dladdr(addr, &info) && info.dli_sname != NULL)
    {
        fprintf(stderr, "%s", info.dli_sname);
    }
    else
    {
        fprintf(stderr, "%p", addr);
    }
}

__attribute__((no_instrument_function))
void __cyg_profile_func_enter(void *func, void *caller)
{
    (void)caller;

    fprintf(stderr, "CALL  ");
    print_function(func);
    fprintf(stderr, "\n");
}

__attribute__((no_instrument_function))
void __cyg_profile_func_exit(void *func, void *caller)
{
    (void)caller;

    fprintf(stderr, "RETURN ");
    print_function(func);
    fprintf(stderr, "\n");
}
