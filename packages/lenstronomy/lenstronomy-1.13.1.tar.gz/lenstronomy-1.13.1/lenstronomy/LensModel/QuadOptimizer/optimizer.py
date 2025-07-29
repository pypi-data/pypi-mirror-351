__author__ = "dgilman"

from scipy.optimize import minimize
import numpy as np
from lenstronomy.Sampling.Samplers.pso import ParticleSwarmOptimizer
from lenstronomy.LensModel.QuadOptimizer.multi_plane_fast import MultiplaneFast
from lenstronomy.Sampling.Pool.pool import choose_pool
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.LensModel.Util.decouple_multi_plane_util import (
    coordinates_and_deflections,
    decoupled_multiplane_class_setup,
    setup_lens_model,
)

__all__ = ["Optimizer"]


class Optimizer(object):
    """Class which executes the optimization routines. Currently implemented as a
    particle swarm optimization followed by a downhill simplex routine.

    Particle swarm optimizer is modified from the CosmoHammer particle swarm routine
    with different convergence criteria implemented.
    """

    def __init__(
        self,
        x_image,
        y_image,
        ray_shooting_class,
        parameter_class,
        tol_source=1e-5,
        tol_simplex_func=1e-6,
        simplex_n_iterations=400,
        pso_convergence_mean=50000,
        particle_swarm=True,
        re_optimize=False,
        re_optimize_scale=1.0,
        kwargs_multiplane_model=None,
    ):
        """

        :param x_image: x-coordinate of image positions
        :param y_image: y-coordinate of image positions
        :param ray_shooting_class: a class with a "ray_shooting" or "ray_shooting_fast" method; for example, an instance of LensModel, or of MultiPlaneFast
        :param parameter_class: a class that handles the lens model parameters being solved for, see classes in param_manager for examples
        :param tol_source: tolerance in the source plane that acts to punish poor solutions of the lens equation
        :param tol_simplex_func: the tolerence for the downhill simplex optimization routine to terminate
        :param simplex_n_iterations: the maximum number of iterations to iterate the downhill simplex optimization
        :param pso_convergence_mean: implements an early termination of the particle swarm optimization when the avergae penalty function hits this value
        :param particle_swarm: bool; if True, performs a particle swarm optimization of the lens model parameters before the downhill simplex routine
        :param re_optimize: bool; if True, initializes the particle swarm cloud in a narrow volume around the initial position
        :param re_optimize_scale: scales the size of the particle swarm cloud if re_optimize is True
        :param kwargs_multiplane_model: keyword arguments passed to MultiPlaneDecoupled if one is using the decoupled multi-plane formalism
        """
        self.x_image = x_image
        self.y_image = y_image
        self.ray_shooting_class = ray_shooting_class
        if callable(getattr(self.ray_shooting_class, "ray_shooting_fast", None)):
            self.ray_shooting_method = self.ray_shooting_class.ray_shooting_fast
        else:
            self.ray_shooting_method = self.ray_shooting_class.ray_shooting
        self._tol_source = tol_source
        self._pso_convergence_mean = pso_convergence_mean
        self._param_class = parameter_class
        self._tol_simplex_func = tol_simplex_func
        self._simplex_n_iterations = simplex_n_iterations
        self._particle_swarm = particle_swarm
        self._re_optimize = re_optimize
        self._re_optimize_scale = re_optimize_scale
        self._kwargs_multiplane_model = kwargs_multiplane_model

    @classmethod
    def decoupled_multiplane(
        cls,
        x_image,
        y_image,
        lens_model,
        kwargs_lens_model,
        index_lens_split,
        parameter_class,
        particle_swarm=True,
        re_optimize=False,
        re_optimize_scale=1.0,
        pso_convergence_mean=50000,
        tol_source=1e-5,
        tol_simplex_func=1e-3,
        simplex_n_iterations=400,
    ):
        """Initializes the Optimizer class using the decoupled multi-plane formalism for
        the lens model and ray shooting methods.

        :param x_image: x_image to fit (should be length 4)
        :param y_image: y_image to fit (should be length 4)
        :param lens_model: an instance of LensModel; should contain all deflectors along the line of sight
        :param kwargs_lens_model: keyword arguments for the LensModel class
        :param index_lens_split: a list of indexes where one splits the lens model, see documentation in Util/decoupled_multiplane_util/decoupled_multiplane_class_setup
        :param parameter_class: a class that handles the lens model parameters being solved for, see classes in param_manager for examples
        :param particle_swarm: bool; if True, performs a particle swarm optimization of the lens model parameters before the downhill simplex routine
        :param re_optimize: bool; if True, initializes the particle swarm cloud in a narrow volume around the initial position
        :param re_optimize_scale: scales the size of the particle swarm cloud if re_optimize is True
        :param pso_convergence_mean: implements an early termination of the particle swarm optimization when the avergae penalty function hits this value
        :param tol_source: tolerance in the source plane that acts to punish poor solutions of the lens equation
        :param tol_simplex_func: the tolerence for the downhill simplex optimization routine to terminate
        :param simplex_n_iterations: the maximum number of iterations to iterate the downhill simplex optimization
        :return: an instance of the Optimizer class using the decoupled multi-plane
         formalism for ray tracing.
        """
        (
            lens_model_fixed,
            lens_model_free,
            kwargs_lens_fixed,
            kwargs_lens_free,
            z_source,
            z_split,
            cosmo_bkg,
        ) = setup_lens_model(lens_model, kwargs_lens_model, index_lens_split)
        (
            x,
            y,
            alpha_x_foreground,
            alpha_y_foreground,
            alpha_beta_subx,
            alpha_beta_suby,
        ) = coordinates_and_deflections(
            lens_model_fixed,
            lens_model_free,
            kwargs_lens_fixed,
            kwargs_lens_free,
            x_image,
            y_image,
            z_split,
            z_source,
            cosmo_bkg,
        )
        npix, interp_points = None, None
        coordinate_type = "MULTIPLE_IMAGES"
        kwargs_decoupled = decoupled_multiplane_class_setup(
            lens_model_free,
            x,
            y,
            alpha_x_foreground,
            alpha_y_foreground,
            alpha_beta_subx,
            alpha_beta_suby,
            z_split,
            coordinate_type,
            interp_points,
            x_image,
            y_image,
        )
        lens_model_decoupled = LensModel(**kwargs_decoupled)
        # we have to reset the keyword arguments of the parameter class here
        parameter_class.kwargs_lens = kwargs_lens_free

        return Optimizer(
            x_image,
            y_image,
            lens_model_decoupled,
            parameter_class,
            tol_source,
            tol_simplex_func,
            simplex_n_iterations,
            pso_convergence_mean,
            particle_swarm,
            re_optimize,
            re_optimize_scale,
            kwargs_decoupled["kwargs_multiplane_model"],
        )

    @classmethod
    def full_raytracing(
        cls,
        x_image,
        y_image,
        lens_model_list,
        redshift_list,
        z_lens,
        z_source,
        parameter_class,
        astropy_instance=None,
        particle_swarm=True,
        re_optimize=False,
        re_optimize_scale=1.0,
        pso_convergence_mean=50000,
        foreground_rays=None,
        tol_source=1e-5,
        tol_simplex_func=1e-3,
        simplex_n_iterations=400,
    ):
        """

        :param x_image: x_image to fit (should be length 4)
        :param y_image: y_image to fit (should be length 4)
        :param lens_model_list: list of lens models for the system
        :param redshift_list: list of lens redshifts for the system
        :param z_lens: the main deflector redshift, the lens models being optimizer must be at this redshift
        :param z_source: the source redshift
        :param parameter_class: an instance of ParamClass (see documentation in QuadOptimizer.param_manager)
        :param astropy_instance: an instance of astropy to pass to the lens model
        :param particle_swarm: bool, whether or not to use a PSO fit first
        :param re_optimize: bool, if True the initial spread of particles will be very tight
        :param re_optimize_scale: float, controls how tight the initial spread of particles is
        :param pso_convergence_mean: when to terminate the PSO fit
        :param foreground_rays: (optional) can pass in pre-computed foreground light rays from a previous fit
         so as to not waste time recomputing them
        :param tol_source: sigma in the source plane chi^2
        :param tol_simplex_func: tolerance for the downhill simplex optimization
        :param simplex_n_iterations: number of iterations per dimension for the downhill simplex optimization
        """

        fast_rayshooting = MultiplaneFast(
            x_image,
            y_image,
            z_lens,
            z_source,
            lens_model_list,
            redshift_list,
            astropy_instance,
            parameter_class,
            foreground_rays,
            tol_source,
        )
        return Optimizer(
            x_image,
            y_image,
            fast_rayshooting,
            parameter_class,
            tol_source,
            tol_simplex_func,
            simplex_n_iterations,
            pso_convergence_mean,
            particle_swarm,
            re_optimize,
            re_optimize_scale,
        )

    @property
    def kwargs_multiplane_model(self):
        """

        :return: the keyword arguments for the decoupled multi-plane class if they are specified
        """
        return self._kwargs_multiplane_model

    def optimize(
        self,
        n_particles=50,
        n_iterations=250,
        verbose=False,
        threadCount=1,
        seed=None,
        minimize_method="Nelder-Mead",
    ):
        """

        :param n_particles: number of PSO particles, will be ignored if self._particle_swarm is False
        :param n_iterations: number of PSO iterations, will be ignored if self._particle_swarm is False
        :param verbose: whether to print stuff
        :param threadCount: integer; number of threads in multi-threading mode
        :param seed: sets a random seed for reproducibility
        :param minimize_method:  optimization algorithm to be used by scipy.optimize.minimize
        :return: keyword arguments that map (x_image, y_image) to the same source coordinate (source_x, source_y)
        """
        if seed is not None:
            np.random.seed(seed)
        if self._particle_swarm:
            if threadCount > 1:
                pool = choose_pool(mpi=False, processes=threadCount)
            else:
                pool = None
            kwargs = self._fit_pso(n_particles, n_iterations, pool, verbose)

        else:
            kwargs = self._param_class.kwargs_lens
        kwargs_lens_final, source_penalty = self._optimization(
            kwargs, verbose, minimize_method
        )
        source_x_array, source_y_array = self.ray_shooting_method(
            self.x_image, self.y_image, kwargs
        )
        source_x, source_y = np.mean(source_x_array), np.mean(source_y_array)

        if verbose:
            print("optimization done.")
            print("Recovered source position: ", (source_x_array, source_y_array))

        return kwargs_lens_final, [source_x, source_y]

    def _fit_pso(self, n_particles, n_iterations, pool, verbose):
        """Executes the PSO."""

        low_bounds, high_bounds = self._param_class.bounds(
            self._re_optimize, self._re_optimize_scale
        )

        pso = ParticleSwarmOptimizer(
            self._logL,
            low_bounds,
            high_bounds,
            n_particles,
            pool,
            args=[self._tol_source],
        )

        args_best, info = pso.optimize(
            n_iterations, verbose, early_stop_tolerance=self._pso_convergence_mean
        )
        kwargs = self._param_class.args_to_kwargs(args_best)
        if verbose:
            print("PSO done... ")
            print(
                "source plane chi^2: ",
                self.source_plane_penalty(args_best),
            )
            print("total chi^2: ", self._penalty_function(args_best))
        return kwargs

    def _optimization(self, kwargs, verbose, method="Nelder-Mead"):
        """
        Executes an optimization routine as specified by method
        :param kwargs: keyword arguments to initialize the optimization
        :param verbose: bool; if True, make print statements
        :param method: optimization algorithm to be used by scipy.optimize.minimize;
        see documentation in scipy: https://docs.scipy.org/doc/scipy/reference/optimize.html#module-scipy.optimize. Can
        also be a callable function with signature method(objective_function, initial_guess). The callable function
        must return a dictionary with the "x" and "fun" properties, as described in the scipy OptimizeResult class docs
        :return: best-fit keyword arguments, and source-plane punishing term used to enforce solution of lens eqn.
        """
        args_init = self._param_class.kwargs_to_args(kwargs)
        if verbose:
            print("starting optimization... ")
        if callable(method):
            opt = method(self._penalty_function, x0=args_init)
        else:
            scipy_options = {
                "adaptive": True,
                "fatol": self._tol_simplex_func,
                "maxiter": self._simplex_n_iterations * len(args_init),
            }
            opt = minimize(
                self._penalty_function,
                x0=args_init,
                method=method,
                options=scipy_options,
            )
        kwargs = self._param_class.args_to_kwargs(opt["x"])
        source_penalty = opt["fun"]
        return kwargs, source_penalty

    def _logL(self, args_lens, *args, **kwargs):
        """

        :param args: array of lens model parameters being optimized, computed from kwargs_lens in a specified
         param_class, see documentation in QuadOptimizer.param_manager
        :return: the log likelihood corresponding to the given chi^2
        """
        chi_square = self._penalty_function(args_lens)
        return -0.5 * chi_square

    def _penalty_function(self, args_lens, *args, **kwargs):
        """This function evaluates a metric that determines goodness of fit.

        :param args_lens: array of parameters that will be turned into keyword arguments
        :return: log-likelihood.
        """
        source_plane_chi2 = self.source_plane_penalty(args_lens)
        param_penalty = self._param_class.param_chi_square_penalty(args_lens)
        return source_plane_chi2 + param_penalty

    def source_plane_penalty(self, args_lens):
        """

        :param args_lens: array of lens model parameters being optimized, computed from kwargs_lens in a specified
         param_class, see documentation in QuadOptimizer.param_manager
        :return: chi2 penalty for the source position (all images must map to the same source coordinate)
        """
        kwargs_lens = self._param_class.args_to_kwargs(args_lens)
        betax, betay = self.ray_shooting_method(self.x_image, self.y_image, kwargs_lens)
        dx_source = (
            (betax[0] - betax[1]) ** 2
            + (betax[0] - betax[2]) ** 2
            + (betax[0] - betax[3]) ** 2
            + (betax[1] - betax[2]) ** 2
            + (betax[1] - betax[3]) ** 2
            + (betax[2] - betax[3]) ** 2
        )
        dy_source = (
            (betay[0] - betay[1]) ** 2
            + (betay[0] - betay[2]) ** 2
            + (betay[0] - betay[3]) ** 2
            + (betay[1] - betay[2]) ** 2
            + (betay[1] - betay[3]) ** 2
            + (betay[2] - betay[3]) ** 2
        )
        chi_square = 0.5 * (dx_source + dy_source) / self._tol_source**2
        return chi_square
