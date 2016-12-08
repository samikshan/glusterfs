#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <urcu/uatomic.h>

#define NFILES         20000    /* total, not per volume */
#define NTHREADS         100
#define NTASKS          ((NFILES * 2) + NTHREADS)

typedef enum { CREATE_TASK, WRITE_AND_DELETE_TASK, EXIT } task_type_t;
typedef struct {
        task_type_t     type;
        int             volume;
        int             file;
} task_t;

char *FILE_PATTERN = "/mnt/glusterfs/mpx%02d/file%d";
task_t task_list[NTASKS];
int next_task = 0;

void
create_tasks (int base, int nvols)
{
        int     f;
        int     v;
        int     t;
        int     i = 0;

        v = 0;
        for (f = 0; f < NFILES; ++f) {
                task_list[i].type = CREATE_TASK;
                task_list[i].volume = base+v;
                task_list[i].file = f;
                ++i;
                v = (v + 1) % nvols;
        }

        v = 0;
        for (f = 0; f < NFILES; ++f) {
                task_list[i].type = WRITE_AND_DELETE_TASK;
                task_list[i].volume = base+v;
                task_list[i].file = f;
                ++i;
                v = (v + 1) % nvols;
        }

        for (t = 0; t < NTHREADS; ++t) {
                task_list[i].type = EXIT;
                ++i;
        }
}

void
create_file (task_t *t)
{
        char    path[1024];
        int     fd;

        sprintf (path, FILE_PATTERN, t->volume, t->file);
        fd = creat (path, 0666);
        if (fd < 0) {
                perror ("creat");
                return;
        }
        close (fd);
}

void
write_file (task_t *t)
{
        char    path[1024];
        int     fd;
        char    buf[4096];

        sprintf (path, FILE_PATTERN, t->volume, t->file);
        fd = open (path, O_WRONLY|O_SYNC);
        if (fd < 0) {
                perror ("open");
                return;
        }
        if (write (fd, buf, sizeof(buf)) < 0) {
                perror ("write");
        }
        close (fd);
        if (unlink (path) < 0) {
                perror ("unlink");
        }
}

void *
worker (void *arg)
{
        int     me      = (int)(long)arg;
        int     i;
        task_t  *t;

        for (;;) {
                i = uatomic_add_return (&next_task, 1);
#if defined(DEBUG)
                printf ("thread %d got %d\n", me, i);
#endif
                if (i > NTASKS) {
                        fprintf (stderr, "%d ran out of tasks\n", me);
                        break;
                }
                t = &task_list[i-1];
                switch (t->type) {
                case CREATE_TASK:
                        create_file (t);
                        break;
                case WRITE_AND_DELETE_TASK:
                        write_file (t);
                        break;
                default:
                        return NULL;
                }
        }

        fprintf (stderr, "%d fell out of loop\n", me);
        return NULL;
}

int
main (int argc, char **argv)
{
        pthread_t       kids[NTHREADS];
        int             i;
        int             ret;

        create_tasks (atoi(argv[1]), atoi(argv[2]));

        for (i = 0; i < NTHREADS; ++i) {
                ret = pthread_create (&kids[i], NULL, worker, (void *)(long)i);
                if (ret != 0) {
                        errno = ret;
                        perror ("pthread_create");
                }
        }

        for (i = 0; i < NTHREADS; ++i) {
                ret = pthread_join (kids[i], NULL);
                if (ret != 0) {
                        errno = ret;
                        perror ("pthread_join");
                }
        }

        return EXIT_SUCCESS;
}
