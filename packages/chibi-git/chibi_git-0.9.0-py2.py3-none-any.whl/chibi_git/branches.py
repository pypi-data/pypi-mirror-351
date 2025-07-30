from chibi_git.obj import Branch, Commit
from chibi_git.command import Git


class Branches:
    def __init__( self, repo ):
        self.repo = repo

    def __repr__( self ):
        return (
            f"Branches( repo={self.repo} )"
        )

    @property
    def local( self ):
        branches = Git.branch( src=self.repo.path ).run()
        result = map( lambda x: Branch( self.repo, x ), branches.result )
        return { b: b for b in result }

    @property
    def remote( self ):
        return Branches_remote( repo=self.repo )
        branches = Git.branch( remote=True, src=self.repo.path ).run()
        result = map( lambda x: Branch( self.repo, x ), branches.result )
        return Branches_remote( result )

    def __iter__( self ):
        return iter( self.local )

    def create( self, name, target=None ):
        """
        crea una nueva rama en el target

        Parameters
        ----------
        name: str
            nombre de la rama nueva
        target: str
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

        command = Git.branch( name, target, src=self.repo.path )
        command.run()
        return self.local[ name ]


class Branches_remote:
    def __init__( self, repo, prefix=None ):
        self.repo = repo
        self.prefix = prefix

    def __repr__( self ):
        return (
            f"Branches_remote( repo={self.repo} )"
        )

    @property
    def origin( self ):
        return Branches_remote( repo=self.repo, prefix='origin' )

    def _get_without_prefix( self, prefix ):
        for branch in self._branches:
            if branch.name.startswith( 'origin' ):
                name = branch.name.replace( 'origin/', '', 1 )
                yield Branch( repo=branch.repo, name=name, is_remote=True )

    def __iter__( self ):
        if self.prefix is not None:
            branches = self._get_without_prefix( self.prefix )
            yield from branches
        else:
            yield from self._branches

    def __getitem__( self, name ):
        for branch in self:
            if name == branch.name:
                return branch
        raise KeyError( 'no se encontro la rama "{name}"' )

    @property
    def _branches( self ):
        branches = Git.branch( remote=True, src=self.repo.path ).run()
        for branch in branches.result:
            yield Branch( repo=self.repo, name=branch, is_remote=True )

    def __getattr__( self, name ):
        try:
            return super().__getattribute__( name )
        except AttributeError as e:
            try:
                return self[ name ]
            except KeyError:
                raise e
