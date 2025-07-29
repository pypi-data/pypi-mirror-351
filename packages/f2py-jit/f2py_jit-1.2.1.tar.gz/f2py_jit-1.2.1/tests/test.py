#!/usr/bin/env python

import os
import unittest
import shutil
import f2py_jit


class Test(unittest.TestCase):

    def setUp(self):
        f2py_jit.clear_modules()
        self.tmp_dir = '/tmp/f2py_jit.d/'
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.mkdir(self.tmp_dir)

    def test_compile_file(self):

        source = os.path.join(os.path.dirname(__file__), 'test_1.f90')
        f2py_jit.compile_module(source, name='jit_test', verbose=False)
        f90 = f2py_jit.import_module('jit_test')
        self.assertTrue('jit_test' in f2py_jit.available_modules())
        out = f90.addone(1)
        self.assertEqual(out, 2)

    def test_build_file_inline(self):
        source_1 = os.path.join(os.path.dirname(__file__), 'test_1.f90')
        source_2 = os.path.join(os.path.dirname(__file__), 'test_2.f90')
        f90 = f2py_jit.build_module([source_1, source_2])
        f90 = f2py_jit.jit([source_1, source_2])
        f90 = f2py_jit.build_module([source_1, source_2], inline=True)
        f90 = f2py_jit.jit([source_1, source_2], inline=True)
        # self.assertTrue('jit_test' in f90)
        # self.assertTrue('mytest2' in f90)

    @unittest.expectedFailure
    def test_verbosity(self):
        source_1 = os.path.join(os.path.dirname(__file__), 'test_1.f90')
        # from numpy.distutils import log
        # log.set_verbosity(-1, force=True)
        f90 = f2py_jit.compile_module("""
module test
int :: x
contains
end module test
""", name='f90')

    def test_compile_source(self):
        source = """
subroutine addone(i, j)
  implicit none
  integer, intent(in) :: i
  integer, intent(out) :: j
  j = i+1
end subroutine addone
"""
        f2py_jit.compile_module(source, name='jit_test_src', verbose=False)
        f90 = f2py_jit.import_module('jit_test_src')
        self.assertTrue('jit_test_src' in f2py_jit.available_modules())
        out = f90.addone(1)
        self.assertEqual(out, 2)

    def test_build_source(self):
        source = """
subroutine addone(i, j)
  implicit none
  integer, intent(in) :: i
  integer, intent(out) :: j
  j = i+1
end subroutine addone
"""
        uid = f2py_jit.build_module(source, 'addone')
        f90 = f2py_jit.import_module(uid)
        out = f90.addone(1)
        self.assertEqual(out, 2)

    def test_jit(self):
        source = """
subroutine addone(i, j)
  implicit none
  integer, intent(in) :: i
  integer, intent(out) :: j
  j = i+1
end subroutine addone
"""
        f90 = f2py_jit.jit(source)
        out = f90.addone(1)
        self.assertEqual(out, 2)

    def test_import_fail(self):
        try:
            f2py_jit.import_module('random_module', quiet=True)
        except (ImportError, ModuleNotFoundError):
            pass
        else:
            self.assertTrue(False)

    def test_two_files(self):
        source_1 = os.path.join(os.path.dirname(__file__), 'test_1.f90')
        source_2 = os.path.join(os.path.dirname(__file__), 'test_2.f90')
        mod_1 = f2py_jit.build_module(source_1)
        mod_2 = f2py_jit.build_module(source_2)
        f90_1 = f2py_jit.import_module(mod_1)
        f90_2 = f2py_jit.import_module(mod_2)
        self.assertTrue(mod_1 in f2py_jit.available_modules())
        self.assertTrue(mod_2 in f2py_jit.available_modules())

        # This should not compile the modules again, so the names will be the same
        new = f2py_jit.build_module(source_1)
        self.assertEqual(new, mod_1)
        new = f2py_jit.build_module(source_2)
        self.assertEqual(new, mod_2)

    def test_fail_compile(self):
        source = """
subroutine addone(i)
  implicit none
  integer, intent(in) :: i, j
  j = i+1
end subroutine addone
"""
        try:
            f2py_jit.compile_module(source, name='jit_test_fail', quiet=True)
        except RuntimeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_inline(self):
        from f2py_jit.finline import inline_source

        source = """
module test

implicit none

contains

subroutine extra(i, j)
  integer, intent(in) :: i
  integer, intent(out) :: j
  integer :: alpha
  alpha = 1
  j = j+alpha
end subroutine extra

subroutine addone(i, j)
  integer, intent(in) :: i
  integer, intent(out) :: j
  integer :: local
  local = 1
  j = i+1
end subroutine addone

subroutine main(output)
  integer, intent(out) :: output
  integer :: input=1
  ! this fails
  ! call addone(1, output)
  call addone(input, output)
  call extra(input, output)
end subroutine main

end module test
"""

        _source = f2py_jit.inline_source(source, ignore='extra')
        self.assertTrue('! inline: addone' in _source)
        self.assertTrue('! inline: extra' not in _source)
        f2py_jit.compile_module(_source, name='jit_test_new', verbose=False)
        f90 = f2py_jit.import_module('jit_test_new')
        out = f90.test.main()
        self.assertEqual(out, 3)

        _source = f2py_jit.inline_source(source, only='extra')
        self.assertTrue('! inline: addone' not in _source)
        self.assertTrue('! inline: extra' in _source)
        f2py_jit.compile_module(_source, name='jit_test_new', verbose=False)
        f90 = f2py_jit.import_module('jit_test_new')
        out = f90.test.main()
        self.assertEqual(out, 3)

    def test_inline_two_modules(self):
        """
        Inlining a function in subroutines with the same name in two
        different modules was buggy.
        """
        source = """
module bare
implicit none
contains

subroutine addone(i, j)
  integer, intent(in) :: i
  integer, intent(out) :: j
  integer :: local
  local = 1
  j = i+1
end subroutine addone

end module bare

module test1
use bare
implicit none
contains

subroutine main(output)
  integer, intent(out) :: output
  integer :: input=1
  call addone(input, output)
end subroutine main

end module test1

module test2
use bare
implicit none
contains

subroutine main(other_output)
  integer, intent(out) :: other_output
  integer :: other_input=1
  call addone(other_input, other_output)
end subroutine main

end module test2
"""

        source = f2py_jit.inline_source(source)
        # print(source)
        f2py_jit.compile_module(source, name='jit_test_two', verbose=False)
        f90 = f2py_jit.import_module('jit_test_two')
        _ = f90.test1.main()
        _ = f90.test2.main()

    def test_jit_inline(self):
        source = """
module test

implicit none

contains

subroutine extra()
  integer :: alpha
  alpha = 1
end subroutine extra

subroutine addone(i, j)
  integer, intent(in) :: i
  integer, intent(out) :: j
  integer :: local
  local = 1
  j = i+1
end subroutine addone

subroutine main(output)
  integer, intent(out) :: output
  integer :: input=1
  ! this fails
  ! call addone(1, output)
  call addone(input, output)
end subroutine main

end module test
"""

        f90 = f2py_jit.jit(f2py_jit.inline(source, ignore='extra'))
        out = f90.test.main()
        self.assertEqual(out, 2)

        f90 = f2py_jit.jit(f2py_jit.inline(source, only='addone'))
        out = f90.test.main()
        self.assertEqual(out, 2)

        f90 = f2py_jit.jit(source, inline=True)
        out = f90.test.main()
        self.assertEqual(out, 2)

    def test_inline_timing(self):
        """
        Check that inlining reduces the execution time
        """
        import time
        from f2py_jit import jit, inline

        source = """
module test

implicit none

contains

subroutine addone(i, j)
  integer, intent(in) :: i
  integer, intent(out) :: j
  integer :: local
  local = 1
  j = int(exp(real(i+local)))
end subroutine addone

subroutine main(nmax,output)
  integer, intent(in) :: nmax
  integer, intent(out) :: output
  integer :: i, k
  do i = 1,nmax
  do k = 1,nmax
  call addone(k, output)
  end do
  end do
end subroutine main

end module test
"""
        source_manual_inline = """
module test

implicit none

contains

subroutine main(nmax,output)
  integer, intent(in) :: nmax
  integer, intent(out) :: output
  integer :: i, k
  integer  :: addone__local
  do i = 1,nmax
  do k = 1,nmax
  addone__local = 1
  output = int ( exp ( real ( k + addone__local ) ) )
  end do
  end do
end subroutine main

end module test
"""
        import f2py_jit
        # f2py_jit.f2py_jit._backend = 'distutils'
        # f2py_jit.f2py_jit._backend = 'meson'
        nmax = 8000

        mod = jit(source_manual_inline)
        t_0 = time.time()
        mod.test.main(nmax)
        dt_manual = time.time() - t_0

        # print(inline(source))
        mod = jit(inline(source))
        t_0 = time.time()
        mod.test.main(nmax)
        dt_inline = time.time() - t_0

        mod = jit(source)
        t_0 = time.time()
        mod.test.main(nmax)
        dt_noinline = time.time() - t_0
        # TODO: this test may fails with meson, inlining slows down :-(
        try:
            import mesonpy
            # self.skipTest('this test may fail with meson')
            if dt_noinline < dt_inline:
                print('inlining is slow with meson', dt_noinline, dt_inline)
        except ImportError:
            self.assertTrue(dt_noinline > dt_inline)

    def test_inline_array_assignment(self):
        import numpy
        from f2py_jit.finline import inline_source

        source = """
subroutine addone(x)
  integer, intent(inout) :: x(:)
  x(:) = x(:) + 1
end subroutine addone

subroutine main(x)
  integer, intent(inout) :: x(:)
  call addone(x)
end subroutine main
"""

        source = f2py_jit.inline_source(source)
        f90 = f2py_jit.jit(source)
        x = numpy.ones(2, dtype='int32')
        out = f90.main(x)
        self.assertEqual(x[0], 2)

    def test_inline_twice(self):
        import numpy
        from f2py_jit.finline import inline_source

        source = """
subroutine addone(y)
  integer, intent(inout) :: y(:)
  integer :: z
  z = 1
  y(:) = y(:) + z
end subroutine addone

subroutine main(x)
  integer, intent(inout) :: x(:)
  call addone(x)
  x = x - 1
  call addone(x)
end subroutine main
"""
        source = f2py_jit.inline_source(source)
        f90 = f2py_jit.jit(source)
        x = numpy.ones(2, dtype='int32')
        out = f90.main(x)
        self.assertEqual(x[0], 2)

    def test_cache(self):
        source = """
subroutine test(i)
  implicit none
  integer, intent(in) :: i
end subroutine test
"""
        fout = self.tmp_dir + '/test.f90'
        with open(fout, 'w') as fh:
            fh.write(source)
        f90 = f2py_jit.jit(fout)
        f90.test(1)

        source = """
subroutine test()
  implicit none
  integer :: i
end subroutine test
"""
        with open(self.tmp_dir + '/test.f90', 'w') as fh:
            fh.write(source)
        f90 = f2py_jit.jit(fout)
        f90.test()

    def test_flags(self):
        source = """
subroutine test()
  k = 1
end subroutine test
"""
        f90 = f2py_jit.jit(source, flags='-O3')
        f90.test()

    def test_module_variable(self):
        source = """
module test
integer :: i = 0
end module test
"""
        f90 = f2py_jit.jit(source)
        f90.test.i = 1
        f90 = f2py_jit.jit(source)
        # print(f90.test.i)
        # self.assertEqual(f90.test.i, 0)

    def test_f90wrap(self):
        try:
            import f90wrap
        except ImportError:
            self.skipTest('no support for derived types')
        import numpy
        src = """
module types

  type array
     double precision, pointer :: x(:) => null()
  end type array

contains

  subroutine new_array(this, x)
    type(array), intent(inout) :: this
    double precision, intent(in), target, optional :: x(:)
    if (present(x)) this % x => x
  end subroutine new_array

end module types
"""
        f90 = f2py_jit.jit(src)
        x = numpy.ones(4)
        a = f90.types.array(x)
        self.assertEqual(a.x[0], 1.)

    def test_string_variable(self):
        source = """
subroutine test(x, y)
  character(*), intent(in) :: x
  integer, intent(out) :: y
  y = len(x)
end subroutine test
"""
        f90 = f2py_jit.jit(source)
        char = 'hello'
        n = f90.test(char)
        self.assertEqual(n, len(char))

    def test_stop(self):
        self.skipTest('')
        source = """
subroutine test()
   stop 'ERROR'
end subroutine test
"""
        import signal

        def handle(num, frame):
            print(num)
            #raise RuntimeError('fortran kernel stopped')

        # signal.signal(signal.SIGCHLD, handle)
        f90 = f2py_jit.jit(source)
        for s in signal.valid_signals():
            #print(s)
            try:
                signal.signal(s, handle)
            except:
                pass
        f90.test()
        #with self.assertRaises(RuntimeError):
        # try:
        #     f90.test()
        # except RuntimeError:
        #     pass

    def tearDown(self):
        import shutil
        f2py_jit.clear_modules()
        shutil.rmtree(self.tmp_dir)


if __name__ == '__main__':
    unittest.main()
