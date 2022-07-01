from . import Command, util


class CopyPlayer(Command):
    def exec(self, arg):
        print(arg.subparser)
        world_dir = util.get_world_path(arg.dir, arg.world)
        save, player = util.get_save_path(world_dir, arg.player)
        print(world_dir, save, player)
