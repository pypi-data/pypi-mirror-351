from chibi_git.command import Git
from chibi_git.obj import Commit, Tag


class Tags:
    def __init__( self, repo ):
        self.repo = repo

    def __repr__( self ):
        return (
            f"Tags( repo={self.repo} )"
        )

    def __iter__( self ):
        tags = Git.tag( src=self.repo.path ).run().result
        return map( lambda x: Tag( repo=self.repo, name=x ), tags )

    def __getitem__( self, name ):
        for tag in self:
            if tag == name:
                return tag
        raise KeyError(
            f'no se encontro el tag "{name}" en {self.repo.path}' )

    def create( self, name, target=None, message=None ):
        """
        crea un nuevo tag en el target

        Parameters
        ----------
        name: str
            nombre de la rama nueva
        target: str, Default:
            objetivo de la rama
        """
        if target is None:
            target = 'HEAD'
        if isinstance( target, Commit ):
            target = str( target )
        if isinstance( target, str ):
            pass
        else:
            raise NotImplementedError(
                f"target {type(target)} con valor {target} no implementado" )

        if message:
            command = Git.tag(
                name, target, '-m', message, src=self.repo.path )
        else:
            command = Git.tag( name, target, src=self.repo.path )
        command.run()
        return self[ name ]
