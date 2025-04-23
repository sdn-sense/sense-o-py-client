import sys

from sense.workflow.base import utils
from sense.workflow.base import state_utils as sutil
from sense.workflow.base.config import WorkflowConfig
from sense.workflow.base.exceptions import ControllerException
from sense.workflow.controller import Controller


def delete_session_if_empty(*, session):
    provider_states = sutil.load_states(session)

    if not provider_states:
        sutil.destroy_session(session)


def manage_workflow(args):
    logger = utils.init_logger()
    config_dir = utils.absolute_path(args.config_dir)
    sessions = sutil.load_sessions()
    config_dir_from_meta = sutil.load_meta_data(args.session, 'config_dir') if args.session in sessions else None

    if config_dir_from_meta and config_dir_from_meta != config_dir:
        logger.error(f"attempt to use session {args.session} from the wrong config dir {config_dir} ...")
        logger.warning(f"ATTN: The CORRECT config dir for session {args.session} is {config_dir_from_meta}!!!!!!!")
        sys.exit(1)

    var_dict = utils.load_vars(args.var_file) if args.var_file else {}

    if args.validate:
        try:
            WorkflowConfig.parse(dir_path=config_dir, var_dict=var_dict)
            logger.info("config looks ok")
        except Exception as e:
            logger.error(f"Validation failed .... {type(e)} {e}")
            logger.error(e, exc_info=True)
            sys.exit(1)

    if args.plan:
        config = WorkflowConfig.parse(dir_path=config_dir, var_dict=var_dict)
        controller = Controller(config=config)
        states = sutil.load_states(args.session)
        controller.init(session=args.session, provider_states=states)
        controller.plan(provider_states=states)
        cr, dl = sutil.dump_plan(resources=controller.resources, to_json=args.json, summary=args.summary)

        logger.warning(f"Applying this plan would create {cr} resource(s) and destroy {dl} resource(s)")
        delete_session_if_empty(session=args.session)
        return

    if args.apply:
        sutil.save_meta_data(dict(config_dir=config_dir), args.session)
        config = WorkflowConfig.parse(dir_path=config_dir, var_dict=var_dict)

        try:
            controller = Controller(config=config)
        except Exception as e:
            logger.error(f"Exceptions while initializing controller .... {e}", exc_info=True)
            sys.exit(1)

        states = sutil.load_states(args.session)

        try:
            controller.init(session=args.session, provider_states=states)
        except Exception as e:
            logger.error(f"Exceptions while initializing providers  .... {e}", exc_info=True)
            sys.exit(1)

        try:
            controller.plan(provider_states=states)
        except Exception as e:
            logger.error(f"Exception while planning ... {e}")
            sys.exit(1)
        except KeyboardInterrupt as kie:
            logger.error(f"Keyboard Interrupt while planning ... {kie}")
            sys.exit(1)

        try:
            controller.add(provider_states=states)
        except Exception as e:
            logger.error(f"Exception while adding ... {e}")
            sys.exit(1)
        except KeyboardInterrupt as kie:
            logger.error(f"Keyboard Interrupt while adding  resources ... {kie}")
            sys.exit(1)

        workflow_failed = False

        try:
            controller.apply(provider_states=states)
        except KeyboardInterrupt as kie:
            logger.error(f"Keyboard Interrupt while creating resources ... {kie}")
            workflow_failed = True
        except ControllerException as ce:
            logger.error(f"Exceptions while creating resources ... {ce}")
            workflow_failed = True
        except Exception as e:
            logger.error(f"Unknown error while creating resources ... {e}")
            workflow_failed = True

        states = controller.get_states()
        services, pending, failed = utils.get_counters(states=states)
        workflow_failed = workflow_failed or pending or failed

        if workflow_failed:
            states = sutil.reconcile_states(states, args.session)

        sutil.save_states(states, args.session)
        logger.info(f"services={services}, pending={pending}, failed={failed}")
        sys.exit(1 if workflow_failed else 0)

    if args.show:
        states = sutil.load_states(args.session) if args.session in sessions else []
        sutil.dump_states(states, args.json, args.summary)
        return

    if args.destroy:
        if args.session not in sessions:
            return

        states = sutil.load_states(args.session)

        if not states:
            sutil.destroy_session(args.session)
            return

        config = WorkflowConfig.parse(dir_path=config_dir, var_dict=var_dict)

        try:
            controller = Controller(config=config)
            controller.init(session=args.session, provider_states=states)
        except Exception as e:
            logger.error(f"Exceptions while initializing controller .... {e}")
            sys.exit(1)

        destroy_failed = False

        try:
            controller.destroy(provider_states=states)
        except ControllerException as e:
            logger.error(f"Exceptions while deleting resources ...{e}")
            destroy_failed = True
        except KeyboardInterrupt as kie:
            logger.error(f"Keyboard Interrupt while deleting resources ... {kie}")
            sys.exit(1)

        if not states:
            logger.info(f"Destroying session {args.session} ...")
            sutil.destroy_session(args.session)
        else:
            sutil.save_states(states, args.session)

        sys.exit(1 if destroy_failed else 0)


def manage_sessions(args):
    if args.show:
        utils.dump_sessions(args.json)
        return


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = utils.build_parser(manage_workflow=manage_workflow,
                                manage_sessions=manage_sessions)
    args = parser.parse_args(argv)

    if len(args.__dict__) == 0:
        parser.print_usage()
        sys.exit(1)

    args.dispatch_func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
