from robot.libraries.BuiltIn import BuiltIn


class AsyncLibrary:
    def __init__(self):
        self._thread_pool = {}
        self._last_thread_handle = 0

    def async_run(self, keyword, *args, **kwargs):
        """
        Executes the provided Robot Framework keyword in a separate
        thread and immediately returns a handle to be used with async_get
        Use:
            ${handle}   Async run   Your keyword "${keyword_attribute}"
        """
        handle = self._last_thread_handle
        thread = self._threaded(keyword, *args, **kwargs)
        thread.start()

        self._thread_pool[handle] = thread
        self._last_thread_handle += 1
        return handle

    def async_get(self, handle):
        """
        Blocks until the thread created by async_run returns
        Use:
            Async get  ${handle}
        """
        assert handle in self._thread_pool, 'Invalid async call handle'
        result = self._thread_pool[handle].result_queue.get()
        del self._thread_pool[handle]
        return result

    def _threaded(self, keyword, *args, **kwargs):
        from queue import Queue
        import threading

        def wrapped_f(q, *args, **kwargs):
            """
            Calls the decorated function and puts the result in a queue
            """
            ret = BuiltIn().run_keyword(keyword, *args, **kwargs)
            q.put(ret)

        q = Queue()
        t = threading.Thread(target=wrapped_f, args=(q,) + args, kwargs=kwargs)
        t.result_queue = q
        return t

