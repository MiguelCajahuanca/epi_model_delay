module epidemic_simulation
  use iso_c_binding, only: c_double
  implicit none

  !-----------------------------------------------------------------------------
  ! Module: epidemic_simulation
  !   Rutina para simular la evolución SIRQD  y escribir
  !   los resultados (T, Muertos, Recuperados, Infectados no detectados,
  !   Infectados detectados, Susceptibles) en un archivo.
  !-----------------------------------------------------------------------------

  ! Parámetros del modelo
  integer, parameter :: NT           = 20                 ! Duración máxima de infección (días)
  integer, parameter :: TFIN         = 200                ! Duración total de la simulación (días)
  real(c_double), parameter :: CI    = 2.0_c_double       ! Tasa de infección
  real(c_double), parameter :: CQ    = 0.5_c_double       ! Factor de detección/cuarenena
  real(c_double), parameter :: CD    = 0.07_c_double      ! Tasa de mortalidad por cohorte
  real(c_double), parameter :: HS    = 0.2_c_double       ! Factor de susceptibilidad
  real(c_double), parameter :: HI    = 0.5_c_double       ! Infectividad en cuarentena
  integer,      parameter :: OUTUNIT = 10                 ! Unidad lógica para salida de archivo

contains

  !----------------------------------------------------------------------------
  !> simulate_and_write
  !! Ejecuta la simulación y escribe la evolución temporal en
  !! results/time_evolution.dat
  !! @param G(0:NT) Distribución de tiempos de generación
  !! @param P(0:NT) Distribución del período de incubación
  !----------------------------------------------------------------------------
  subroutine simulate_and_write(G, P) bind(C)
    implicit none
    real(c_double), intent(in)  :: G(0:NT), P(0:NT)
    real(c_double)             :: I(0:NT) = 0.0_c_double   ! Cohortes de infectados no detectados
    real(c_double)             :: Q(0:NT) = 0.0_c_double   ! Cohortes de infectados detectados
    real(c_double)             :: S      = 1.0_c_double - 1.0e-6_c_double  ! Susceptibles
    real(c_double)             :: R      = 0.0_c_double   ! Recuperados totales
    real(c_double)             :: D      = 0.0_c_double   ! Muertos totales
    real(c_double)             :: AA, BB, DQ, CONT        ! Variables temporales
    integer                    :: T, KT

    ! Inicialización de la primera infección
    I(0) = 1.0e-6_c_double

    ! Abrir archivo de salida (reemplaza contenido)
    open(unit=OUTUNIT, file="results/time_evolution.dat", &
         status="replace", action="write", form="formatted")
    write(OUTUNIT, '(A)') " #  T    D        R        I        Q        S"

    ! Bucle principal de tiempo
    do T = 0, TFIN

      !------ 1) Cálculo de muertes y recuperaciones de la cohorte NT
      AA = (I(NT) + HI * Q(NT)) * CD
      BB = I(NT) * (1.0_c_double - CD) + Q(NT) * (1.0_c_double - CD * HI)
      D  = D + AA
      R  = R + BB

      !------ 2) Avanzar todas las cohortes un día
      do KT = NT-1, 0, -1
        I(KT+1) = I(KT)
        Q(KT+1) = Q(KT)
      end do

      !------ 3) Nueva infecciones según la distribución G
      AA = 0.0_c_double
      do KT = 0, NT
        AA = AA + G(KT) * (I(KT) + HS * Q(KT))
      end do
      I(0) = S * CI * AA
      Q(0) = 0.0_c_double
      S    = S - I(0)

      !------ 4) Transición I -> Q según la distribución P
      do KT = 0, NT
        CONT = min(1.0_c_double, P(KT) * CQ)
        DQ   = I(KT) * CONT
        I(KT) = I(KT) - DQ
        Q(KT) = Q(KT) + DQ
      end do

      !------ 5) Escribir estado actual en archivo
      write(OUTUNIT, '(I4,1X,F10.6,1X,F10.6,1X,F10.6,1X,F10.6,1X,F10.6)') &
            T, D, R, sum(I), sum(Q), S
    end do

    close(OUTUNIT)
  end subroutine simulate_and_write

end module epidemic_simulation
