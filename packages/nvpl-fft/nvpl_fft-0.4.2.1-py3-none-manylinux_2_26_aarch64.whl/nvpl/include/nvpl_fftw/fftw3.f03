  integer(C_INT), parameter :: FFTW_R2HC = 0
  integer(C_INT), parameter :: FFTW_HC2R = 1
  integer(C_INT), parameter :: FFTW_DHT = 2
  integer(C_INT), parameter :: FFTW_REDFT00 = 3
  integer(C_INT), parameter :: FFTW_REDFT01 = 4
  integer(C_INT), parameter :: FFTW_REDFT10 = 5
  integer(C_INT), parameter :: FFTW_REDFT11 = 6
  integer(C_INT), parameter :: FFTW_RODFT00 = 7
  integer(C_INT), parameter :: FFTW_RODFT01 = 8
  integer(C_INT), parameter :: FFTW_RODFT10 = 9
  integer(C_INT), parameter :: FFTW_RODFT11 = 10

  integer(C_INT), parameter :: FFTW_FORWARD = -1
  integer(C_INT), parameter :: FFTW_BACKWARD = +1

  integer(C_INT), parameter :: FFTW_MEASURE = 0
  integer(C_INT), parameter :: FFTW_DESTROY_INPUT = 1
  integer(C_INT), parameter :: FFTW_UNALIGNED = 2
  integer(C_INT), parameter :: FFTW_CONSERVE_MEMORY = 4
  integer(C_INT), parameter :: FFTW_EXHAUSTIVE = 8
  integer(C_INT), parameter :: FFTW_PRESERVE_INPUT = 16
  integer(C_INT), parameter :: FFTW_PATIENT = 32
  integer(C_INT), parameter :: FFTW_ESTIMATE = 64
  integer(C_INT), parameter :: FFTW_WISDOM_ONLY = 2097152
  integer(C_INT), parameter :: FFTW_ESTIMATE_PATIENT = 128
  integer(C_INT), parameter :: FFTW_BELIEVE_PCOST = 256
  integer(C_INT), parameter :: FFTW_NO_DFT_R2HC = 512
  integer(C_INT), parameter :: FFTW_NO_NONTHREADED = 1024
  integer(C_INT), parameter :: FFTW_NO_BUFFERING = 2048
  integer(C_INT), parameter :: FFTW_NO_INDIRECT_OP = 4096
  integer(C_INT), parameter :: FFTW_ALLOW_LARGE_GENERIC = 8192
  integer(C_INT), parameter :: FFTW_NO_RANK_SPLITS = 16384
  integer(C_INT), parameter :: FFTW_NO_VRANK_SPLITS = 32768
  integer(C_INT), parameter :: FFTW_NO_VRECURSE = 65536
  integer(C_INT), parameter :: FFTW_NO_SIMD = 131072
  integer(C_INT), parameter :: FFTW_NO_SLOW = 262144
  integer(C_INT), parameter :: FFTW_NO_FIXED_RADIX_LARGE_N = 524288
  integer(C_INT), parameter :: FFTW_ALLOW_PRUNING = 1048576

  type, bind(C) :: fftw_iodim
    integer(C_INT) n, is, os
  end type fftw_iodim
  type, bind(C) :: fftw_iodim64
    integer(C_INTPTR_T) n, is, os
  end type fftw_iodim64

  type, bind(C) :: fftwf_iodim
    integer(C_INT) n, is, os
  end type fftwf_iodim
  type, bind(C) :: fftwf_iodim64
    integer(C_INTPTR_T) n, is, os
  end type fftwf_iodim64

  ! -----------------------
  ! Version Information
  ! -----------------------

  interface nvpl_fft_get_version
    integer(C_INT) function nvpl_fft_get_version() &
    bind(C, name='nvpl_fft_get_version')
    import
    end function nvpl_fft_get_version
  end interface nvpl_fft_get_version

  ! -----------------------
  ! Basic plan interface
  ! -----------------------

  ! Complex input to complex output (C2C)

  interface fftw_plan_dft_1d
    type(C_PTR) function fftw_plan_dft_1d(n0,in,out,sign,flags) &
    bind(C, name='fftw_plan_dft_1d')
    import
      integer(C_INT), value :: n0
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftw_plan_dft_1d
  end interface fftw_plan_dft_1d

  interface fftw_plan_dft_2d
    type(C_PTR) function fftw_plan_dft_2d(n0,n1,in,out,sign,flags) &
    bind(C, name='fftw_plan_dft_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftw_plan_dft_2d
  end interface fftw_plan_dft_2d

  interface fftw_plan_dft_3d
    type(C_PTR) function fftw_plan_dft_3d(n0,n1,n2,in,out,sign,flags) &
    bind(C, name='fftw_plan_dft_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftw_plan_dft_3d
  end interface fftw_plan_dft_3d

  interface fftw_plan_dft
    type(C_PTR) function fftw_plan_dft(rank,n,in,out,sign,flags) &
    bind(C, name='fftw_plan_dft')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftw_plan_dft
  end interface fftw_plan_dft

  interface fftwf_plan_dft_1d
    type(C_PTR) function fftwf_plan_dft_1d(n0,in,out,sign,flags) &
    bind(C, name='fftwf_plan_dft_1d')
    import
      integer(C_INT), value :: n0
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_1d
  end interface fftwf_plan_dft_1d

  interface fftwf_plan_dft_2d
    type(C_PTR) function fftwf_plan_dft_2d(n0,n1,in,out,sign,flags) &
    bind(C, name='fftwf_plan_dft_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_2d
  end interface fftwf_plan_dft_2d

  interface fftwf_plan_dft_3d
    type(C_PTR) function fftwf_plan_dft_3d(n0,n1,n2,in,out,sign,flags) &
    bind(C, name='fftwf_plan_dft_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_3d
  end interface fftwf_plan_dft_3d

  interface fftwf_plan_dft
    type(C_PTR) function fftwf_plan_dft(rank,n,in,out,sign,flags) &
    bind(C, name='fftwf_plan_dft')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftwf_plan_dft
  end interface fftwf_plan_dft

  ! Real input to complex output (R2C)

  interface fftw_plan_dft_r2c_1d
    type(C_PTR) function fftw_plan_dft_r2c_1d(n0,in,out,flags) &
    bind(C, name='fftw_plan_dft_r2c_1d')
    import
      integer(C_INT), value :: n0
      real(C_DOUBLE), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_r2c_1d
  end interface fftw_plan_dft_r2c_1d

  interface fftw_plan_dft_r2c_2d
    type(C_PTR) function fftw_plan_dft_r2c_2d(n0,n1,in,out,flags) &
    bind(C, name='fftw_plan_dft_r2c_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      real(C_DOUBLE), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_r2c_2d
  end interface fftw_plan_dft_r2c_2d

  interface fftw_plan_dft_r2c_3d
    type(C_PTR) function fftw_plan_dft_r2c_3d(n0,n1,n2,in,out,flags) &
    bind(C, name='fftw_plan_dft_r2c_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      real(C_DOUBLE), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_r2c_3d
  end interface fftw_plan_dft_r2c_3d

  interface fftw_plan_dft_r2c
    type(C_PTR) function fftw_plan_dft_r2c(rank,n,in,out,flags) &
    bind(C, name='fftw_plan_dft_r2c')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      real(C_DOUBLE), dimension(*), intent(out) :: in
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_r2c
  end interface fftw_plan_dft_r2c

  interface fftwf_plan_dft_r2c_1d
    type(C_PTR) function fftwf_plan_dft_r2c_1d(n0,in,out,flags) &
    bind(C, name='fftwf_plan_dft_r2c_1d')
    import
      integer(C_INT), value :: n0
      real(C_FLOAT), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_r2c_1d
  end interface fftwf_plan_dft_r2c_1d

  interface fftwf_plan_dft_r2c_2d
    type(C_PTR) function fftwf_plan_dft_r2c_2d(n0,n1,in,out,flags) &
    bind(C, name='fftwf_plan_dft_r2c_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      real(C_FLOAT), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_r2c_2d
  end interface fftwf_plan_dft_r2c_2d

  interface fftwf_plan_dft_r2c_3d
    type(C_PTR) function fftwf_plan_dft_r2c_3d(n0,n1,n2,in,out,flags) &
    bind(C, name='fftwf_plan_dft_r2c_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      real(C_FLOAT), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_r2c_3d
  end interface fftwf_plan_dft_r2c_3d

  interface fftwf_plan_dft_r2c
    type(C_PTR) function fftwf_plan_dft_r2c(rank,n,in,out,flags) &
    bind(C, name='fftwf_plan_dft_r2c')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      real(C_FLOAT), dimension(*), intent(out) :: in
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_r2c
  end interface fftwf_plan_dft_r2c

  ! Complex input to real output (C2R)

  interface fftw_plan_dft_c2r_1d
    type(C_PTR) function fftw_plan_dft_c2r_1d(n0,in,out,flags) &
    bind(C, name='fftw_plan_dft_c2r_1d')
    import
      integer(C_INT), value :: n0
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      real(C_DOUBLE), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_c2r_1d
  end interface fftw_plan_dft_c2r_1d

  interface fftw_plan_dft_c2r_2d
    type(C_PTR) function fftw_plan_dft_c2r_2d(n0,n1,in,out,flags) &
    bind(C, name='fftw_plan_dft_c2r_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      real(C_DOUBLE), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_c2r_2d
  end interface fftw_plan_dft_c2r_2d

  interface fftw_plan_dft_c2r_3d
    type(C_PTR) function fftw_plan_dft_c2r_3d(n0,n1,n2,in,out,flags) &
    bind(C, name='fftw_plan_dft_c2r_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      real(C_DOUBLE), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_c2r_3d
  end interface fftw_plan_dft_c2r_3d

  interface fftw_plan_dft_c2r
    type(C_PTR) function fftw_plan_dft_c2r(rank,n,in,out,flags) &
    bind(C, name='fftw_plan_dft_c2r')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      real(C_DOUBLE), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftw_plan_dft_c2r
  end interface fftw_plan_dft_c2r

  interface fftwf_plan_dft_c2r_1d
    type(C_PTR) function fftwf_plan_dft_c2r_1d(n0,in,out,flags) &
    bind(C, name='fftwf_plan_dft_c2r_1d')
    import
      integer(C_INT), value :: n0
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      real(C_FLOAT), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_c2r_1d
  end interface fftwf_plan_dft_c2r_1d

  interface fftwf_plan_dft_c2r_2d
    type(C_PTR) function fftwf_plan_dft_c2r_2d(n0,n1,in,out,flags) &
    bind(C, name='fftwf_plan_dft_c2r_2d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      real(C_FLOAT), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_c2r_2d
  end interface fftwf_plan_dft_c2r_2d

  interface fftwf_plan_dft_c2r_3d
    type(C_PTR) function fftwf_plan_dft_c2r_3d(n0,n1,n2,in,out,flags) &
    bind(C, name='fftwf_plan_dft_c2r_3d')
    import
      integer(C_INT), value :: n0
      integer(C_INT), value :: n1
      integer(C_INT), value :: n2
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      real(C_FLOAT), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_c2r_3d
  end interface fftwf_plan_dft_c2r_3d

  interface fftwf_plan_dft_c2r
    type(C_PTR) function fftwf_plan_dft_c2r(rank,n,in,out,flags) &
    bind(C, name='fftwf_plan_dft_c2r')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      real(C_FLOAT), dimension(*), intent(out) :: out
      integer(C_INT), value :: flags
    end function fftwf_plan_dft_c2r
  end interface fftwf_plan_dft_c2r

  ! -----------------------
  ! Advanced plan interface
  ! -----------------------

  interface fftw_plan_many_dft
    type(C_PTR) function fftw_plan_many_dft(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,sign,flags) &
    bind(C, name='fftw_plan_many_dft')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftw_plan_many_dft
  end interface fftw_plan_many_dft

  interface fftw_plan_many_dft_r2c
    type(C_PTR) function fftw_plan_many_dft_r2c(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,flags) &
    bind(C, name='fftw_plan_many_dft_r2c')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      real(C_DOUBLE), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: flags
    end function fftw_plan_many_dft_r2c
  end interface fftw_plan_many_dft_r2c

  interface fftw_plan_many_dft_c2r
    type(C_PTR) function fftw_plan_many_dft_c2r(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,flags) &
    bind(C, name='fftw_plan_many_dft_c2r')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      real(C_DOUBLE), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: flags
    end function fftw_plan_many_dft_c2r
  end interface fftw_plan_many_dft_c2r

  interface fftwf_plan_many_dft
    type(C_PTR) function fftwf_plan_many_dft(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,sign,flags) &
    bind(C, name='fftwf_plan_many_dft')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: sign
      integer(C_INT), value :: flags
    end function fftwf_plan_many_dft
  end interface fftwf_plan_many_dft

  interface fftwf_plan_many_dft_r2c
    type(C_PTR) function fftwf_plan_many_dft_r2c(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,flags) &
    bind(C, name='fftwf_plan_many_dft_r2c')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      real(C_FLOAT), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: flags
    end function fftwf_plan_many_dft_r2c
  end interface fftwf_plan_many_dft_r2c

  interface fftwf_plan_many_dft_c2r
    type(C_PTR) function fftwf_plan_many_dft_c2r(rank,n,howmany,in,inembed,istride,idist,out,onembed,ostride,odist,flags) &
    bind(C, name='fftwf_plan_many_dft_c2r')
    import
      integer(C_INT), value :: rank
      integer(C_INT), dimension(*), intent(in) :: n
      integer(C_INT), value :: howmany
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: in
      integer(C_INT), dimension(*), intent(in) :: inembed
      integer(C_INT), value :: istride
      integer(C_INT), value :: idist
      real(C_FLOAT), dimension(*), intent(out) :: out
      integer(C_INT), dimension(*), intent(in) :: onembed
      integer(C_INT), value :: ostride
      integer(C_INT), value :: odist
      integer(C_INT), value :: flags
    end function fftwf_plan_many_dft_c2r
  end interface fftwf_plan_many_dft_c2r

  ! -----------------------
  ! Execute interface
  ! -----------------------

  interface fftw_execute
    subroutine fftw_execute(plan) &
    bind(C, name='fftw_execute')
    import
      type(C_PTR), value :: plan
    end subroutine fftw_execute
  end interface fftw_execute

  interface fftwf_execute
    subroutine fftwf_execute(plan) &
    bind(C, name='fftwf_execute')
    import
      type(C_PTR), value :: plan
    end subroutine fftwf_execute
  end interface fftwf_execute

  interface fftw_execute_dft
    subroutine fftw_execute_dft(plan,idata,odata) &
    bind(C, name='fftw_execute_dft')
    import
      type(C_PTR), value :: plan
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(inout) :: idata
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: odata
    end subroutine fftw_execute_dft
  end interface fftw_execute_dft

  interface fftw_execute_dft_r2c
    subroutine fftw_execute_dft_r2c(plan,idata,odata) &
    bind(C, name='fftw_execute_dft_r2c')
    import
      type(C_PTR), value :: plan
      real(C_DOUBLE), dimension(*), intent(inout) :: idata
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(out) :: odata
    end subroutine fftw_execute_dft_r2c
  end interface fftw_execute_dft_r2c

  interface fftw_execute_dft_c2r
    subroutine fftw_execute_dft_c2r(plan,idata,odata) &
    bind(C, name='fftw_execute_dft_c2r')
    import
      type(C_PTR), value :: plan
      complex(C_DOUBLE_COMPLEX), dimension(*), intent(inout) :: idata
      real(C_DOUBLE), dimension(*), intent(out) :: odata
    end subroutine fftw_execute_dft_c2r
  end interface fftw_execute_dft_c2r

  interface fftwf_execute_dft
    subroutine fftwf_execute_dft(plan,idata,odata) &
    bind(C, name='fftwf_execute_dft')
    import
      type(C_PTR), value :: plan
      complex(C_FLOAT_COMPLEX), dimension(*), intent(inout) :: idata
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: odata
    end subroutine fftwf_execute_dft
  end interface fftwf_execute_dft

  interface fftwf_execute_dft_r2c
    subroutine fftwf_execute_dft_r2c(plan,idata,odata) &
    bind(C, name='fftwf_execute_dft_r2c')
    import
      type(C_PTR), value :: plan
      real(C_FLOAT), dimension(*), intent(inout) :: idata
      complex(C_FLOAT_COMPLEX), dimension(*), intent(out) :: odata
    end subroutine fftwf_execute_dft_r2c
  end interface fftwf_execute_dft_r2c

  interface fftwf_execute_dft_c2r
    subroutine fftwf_execute_dft_c2r(plan,idata,odata) &
    bind(C, name='fftwf_execute_dft_c2r')
    import
      type(C_PTR), value :: plan
      complex(C_FLOAT_COMPLEX), dimension(*), intent(inout) :: idata
      real(C_FLOAT), dimension(*), intent(out) :: odata
    end subroutine fftwf_execute_dft_c2r
  end interface fftwf_execute_dft_c2r

  ! -----------------------
  ! Destruction interface
  ! -----------------------

  interface fftw_destroy_plan
    subroutine fftw_destroy_plan(plan) &
    bind(C, name='fftw_destroy_plan')
    import
      type(C_PTR), value :: plan
    end subroutine fftw_destroy_plan
  end interface fftw_destroy_plan

  interface fftwf_destroy_plan
    subroutine fftwf_destroy_plan(plan) &
    bind(C, name='fftwf_destroy_plan')
    import
      type(C_PTR), value :: plan
    end subroutine fftwf_destroy_plan
  end interface fftwf_destroy_plan

  ! -----------------------
  ! Thread control
  ! -----------------------

  interface fftw_init_threads
    integer(C_INT) function fftw_init_threads() &
    bind(C, name='fftw_init_threads')
    import
    end function fftw_init_threads
  end interface fftw_init_threads

  interface fftwf_init_threads
    integer(C_INT) function fftwf_init_threads() &
    bind(C, name='fftwf_init_threads')
    import
    end function fftwf_init_threads
  end interface fftwf_init_threads

  interface fftw_plan_with_nthreads
    subroutine fftw_plan_with_nthreads(nthreads) &
    bind(C, name='fftw_plan_with_nthreads')
    import
      integer(C_INT), value :: nthreads
    end subroutine fftw_plan_with_nthreads
  end interface fftw_plan_with_nthreads

  interface fftwf_plan_with_nthreads
    subroutine fftwf_plan_with_nthreads(nthreads) &
    bind(C, name='fftwf_plan_with_nthreads')
    import
      integer(C_INT), value :: nthreads
    end subroutine fftwf_plan_with_nthreads
  end interface fftwf_plan_with_nthreads

  interface fftw_planner_nthreads
    integer(C_INT) function fftw_planner_nthreads() &
    bind(C, name='fftw_planner_nthreads')
    import
    end function fftw_planner_nthreads
  end interface fftw_planner_nthreads

  interface fftwf_planner_nthreads
    integer(C_INT) function fftwf_planner_nthreads() &
    bind(C, name='fftwf_planner_nthreads')
    import
    end function fftwf_planner_nthreads
  end interface fftwf_planner_nthreads

  interface fftw_cleanup_threads
    subroutine fftw_cleanup_threads() &
    bind(C, name='fftw_cleanup_threads')
    import
    end subroutine fftw_cleanup_threads
  end interface fftw_cleanup_threads

  interface fftwf_cleanup_threads
    subroutine fftwf_cleanup_threads() &
    bind(C, name='fftwf_cleanup_threads')
    import
    end subroutine fftwf_cleanup_threads
  end interface fftwf_cleanup_threads

  ! -----------------------
  ! Other
  ! -----------------------

  interface fftw_cleanup
    subroutine fftw_cleanup() &
    bind(C, name='fftw_cleanup')
    import
    end subroutine fftw_cleanup
  end interface fftw_cleanup

  interface fftwf_cleanup
    subroutine fftwf_cleanup() &
    bind(C, name='fftwf_cleanup')
    import
    end subroutine fftwf_cleanup
  end interface fftwf_cleanup

  interface fftw_print_plan
    subroutine fftw_print_plan(plan) bind(C, name='fftw_print_plan')
    import
      type(C_PTR), value :: plan
    end subroutine fftw_print_plan
  end interface fftw_print_plan

  interface fftwf_print_plan
    subroutine fftwf_print_plan(plan) &
    bind(C, name='fftwf_print_plan')
    import
      type(C_PTR), value :: plan
    end subroutine fftwf_print_plan
  end interface fftwf_print_plan

  interface fftw_set_timelimit
    subroutine fftw_set_timelimit(seconds) &
    bind(C, name='fftw_set_timelimit')
    import
      real(C_DOUBLE), value :: seconds
    end subroutine fftw_set_timelimit
  end interface fftw_set_timelimit

  interface fftwf_set_timelimit
    subroutine fftwf_set_timelimit(seconds) &
    bind(C, name='fftwf_set_timelimit')
    import
      real(C_DOUBLE), value :: seconds
    end subroutine fftwf_set_timelimit
  end interface fftwf_set_timelimit

  interface fftw_cost
    real(C_DOUBLE) function fftw_cost(plan) &
    bind(C, name='fftw_cost')
    import
      type(C_PTR), value :: plan
    end function fftw_cost
  end interface fftw_cost

  interface fftwf_cost
    real(C_DOUBLE) function fftwf_cost(plan) &
    bind(C, name='fftwf_cost')
    import
      type(C_PTR), value :: plan
    end function fftwf_cost
  end interface fftwf_cost

  interface fftw_flops
    subroutine fftw_flops(plan,add,mul,fma) &
    bind(C, name='fftw_flops')
    import
      type(C_PTR), value :: plan
      real(C_DOUBLE), dimension(*), intent(out) :: add
      real(C_DOUBLE), dimension(*), intent(out) :: mul
      real(C_DOUBLE), dimension(*), intent(out) :: fma
    end subroutine fftw_flops
  end interface fftw_flops

  interface fftwf_flops
    subroutine fftwf_flops(plan,add,mul,fma) &
    bind(C, name='fftwf_flops')
    import
      type(C_PTR), value :: plan
      real(C_DOUBLE), dimension(*), intent(out) :: add
      real(C_DOUBLE), dimension(*), intent(out) :: mul
      real(C_DOUBLE), dimension(*), intent(out) :: fma
    end subroutine fftwf_flops
  end interface fftwf_flops

  ! -----------------------
  ! Wisdom interface
  ! -----------------------

  interface fftw_export_wisdom
    subroutine fftw_export_wisdom(write_char,data) &
    bind(C, name='fftw_export_wisdom')
    import
      type(C_FUNPTR), value :: write_char
      type(C_PTR), value :: data
    end subroutine fftw_export_wisdom
  end interface fftw_export_wisdom

  interface fftw_export_wisdom_to_file
    subroutine fftw_export_wisdom_to_file(output_file) &
    bind(C, name='fftw_export_wisdom_to_file')
    import
      type(C_PTR), value :: output_file
    end subroutine fftw_export_wisdom_to_file
  end interface fftw_export_wisdom_to_file

  interface fftw_export_wisdom_to_string
    type(C_PTR) function fftw_export_wisdom_to_string() &
    bind(C, name='fftw_export_wisdom_to_string')
    import
    end function fftw_export_wisdom_to_string
  end interface fftw_export_wisdom_to_string

  interface fftw_import_wisdom
    integer(C_INT) function fftw_import_wisdom(read_char,data) &
    bind(C, name='fftw_import_wisdom')
    import
      type(C_FUNPTR), value :: read_char
      type(C_PTR), value :: data
    end function fftw_import_wisdom
  end interface fftw_import_wisdom

  interface fftw_import_wisdom_from_file
    integer(C_INT) function fftw_import_wisdom_from_file(input_file) &
    bind(C, name='fftw_import_wisdom_from_file')
    import
      type(C_PTR), value :: input_file
    end function fftw_import_wisdom_from_file
  end interface fftw_import_wisdom_from_file

  interface fftw_import_wisdom_from_string
    integer(C_INT) function fftw_import_wisdom_from_string(input_string) &
    bind(C, name='fftw_import_wisdom_from_string')
    import
      character(C_CHAR), dimension(*), intent(in) :: input_string
    end function fftw_import_wisdom_from_string
  end interface fftw_import_wisdom_from_string

  interface fftw_import_system_wisdom
    integer(C_INT) function fftw_import_system_wisdom() &
    bind(C, name='fftw_import_system_wisdom')
    import
    end function fftw_import_system_wisdom
  end interface fftw_import_system_wisdom

  interface fftw_forget_wisdom
    subroutine fftw_forget_wisdom() &
    bind(C, name='fftw_forget_wisdom')
    import
    end subroutine fftw_forget_wisdom
  end interface fftw_forget_wisdom

  interface fftwf_export_wisdom
    subroutine fftwf_export_wisdom(write_char,data) &
    bind(C, name='fftwf_export_wisdom')
    import
      type(C_FUNPTR), value :: write_char
      type(C_PTR), value :: data
    end subroutine fftwf_export_wisdom
  end interface fftwf_export_wisdom

  interface fftwf_export_wisdom_to_file
    subroutine fftwf_export_wisdom_to_file(output_file) &
    bind(C, name='fftwf_export_wisdom_to_file')
    import
      type(C_PTR), value :: output_file
    end subroutine fftwf_export_wisdom_to_file
  end interface fftwf_export_wisdom_to_file

  interface fftwf_export_wisdom_to_string
    type(C_PTR) function fftwf_export_wisdom_to_string() &
    bind(C, name='fftwf_export_wisdom_to_string')
    import
    end function fftwf_export_wisdom_to_string
  end interface fftwf_export_wisdom_to_string

  interface fftwf_import_wisdom
    integer(C_INT) function fftwf_import_wisdom(read_char,data) &
    bind(C, name='fftwf_import_wisdom')
    import
      type(C_FUNPTR), value :: read_char
      type(C_PTR), value :: data
    end function fftwf_import_wisdom
  end interface fftwf_import_wisdom

  interface fftwf_import_wisdom_from_file
    integer(C_INT) function fftwf_import_wisdom_from_file(input_file) &
    bind(C, name='fftwf_import_wisdom_from_file')
    import
      type(C_PTR), value :: input_file
    end function fftwf_import_wisdom_from_file
  end interface fftwf_import_wisdom_from_file

  interface fftwf_import_wisdom_from_string
    integer(C_INT) function fftwf_import_wisdom_from_string(input_string) &
    bind(C, name='fftwf_import_wisdom_from_string')
    import
      character(C_CHAR), dimension(*), intent(in) :: input_string
    end function fftwf_import_wisdom_from_string
  end interface  fftwf_import_wisdom_from_string

  interface fftwf_import_system_wisdom
    integer(C_INT) function fftwf_import_system_wisdom() &
    bind(C, name='fftwf_import_system_wisdom')
    import
    end function fftwf_import_system_wisdom
  end interface fftwf_import_system_wisdom

  interface fftwf_forget_wisdom
    subroutine fftwf_forget_wisdom() &
    bind(C, name='fftwf_forget_wisdom')
    import
    end subroutine fftwf_forget_wisdom
  end interface fftwf_forget_wisdom

  ! -----------------------
  ! Memory interface
  ! -----------------------

  interface fftw_alignment_of
    integer(C_INT) function fftw_alignment_of(p) &
    bind(C, name='fftw_alignment_of')
    import
      real(C_DOUBLE), dimension(*), intent(out) :: p
    end function fftw_alignment_of
  end interface fftw_alignment_of

  interface fftw_alloc_complex
    type(C_PTR) function fftw_alloc_complex(n) &
    bind(C, name='fftw_alloc_complex')
    import
      integer(C_SIZE_T), value :: n
    end function fftw_alloc_complex
  end interface fftw_alloc_complex

  interface fftw_alloc_real
    type(C_PTR) function fftw_alloc_real(n) &
    bind(C, name='fftw_alloc_real')
    import
      integer(C_SIZE_T), value :: n
    end function fftw_alloc_real
  end interface fftw_alloc_real

  interface fftw_free
    subroutine fftw_free(p) &
    bind(C, name='fftw_free')
    import
      type(C_PTR), value :: p
    end subroutine fftw_free
  end interface fftw_free
 
  interface fftw_malloc
    type(C_PTR) function fftw_malloc(n) &
    bind(C, name='fftw_malloc')
    import
      integer(C_SIZE_T), value :: n
    end function fftw_malloc
  end interface fftw_malloc

  interface fftwf_alignment_of
    integer(C_INT) function fftwf_alignment_of(p) &
    bind(C, name='fftwf_alignment_of')
    import
      real(C_FLOAT), dimension(*), intent(out) :: p
    end function fftwf_alignment_of
  end interface fftwf_alignment_of

  interface fftwf_alloc_complex
    type(C_PTR) function fftwf_alloc_complex(n) &
    bind(C, name='fftwf_alloc_complex')
    import
      integer(C_SIZE_T), value :: n
    end function fftwf_alloc_complex
  end interface fftwf_alloc_complex

  interface fftwf_alloc_real
    type(C_PTR) function fftwf_alloc_real(n) &
    bind(C, name='fftwf_alloc_real')
    import
      integer(C_SIZE_T), value :: n
    end function fftwf_alloc_real
  end interface fftwf_alloc_real

  interface fftwf_free
    subroutine fftwf_free(p) &
    bind(C, name='fftwf_free')
    import
      type(C_PTR), value :: p
    end subroutine fftwf_free
  end interface fftwf_free

  interface fftwf_malloc
    type(C_PTR) function fftwf_malloc(n) &
    bind(C, name='fftwf_malloc')
    import
      integer(C_SIZE_T), value :: n
    end function fftwf_malloc
  end interface fftwf_malloc
 