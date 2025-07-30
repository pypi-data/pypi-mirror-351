import typing


class FabricItem:
    def __init__(self, alias_name: str, endpoints: typing.Dict[str, typing.Dict[str, str]]):
        """Don't worry about using the constructor to create an instance of this class. Fabric will automatically create it for you (as long as you follow the steps within `Remarks`).

        :param alias_name: The alias for the data source being connected to, configured in the portal.
        :type alias_name: str
        :param endpoints: The different endpoints for the data source.
        :type endpoints: typing.Dict[str, typing.Dict[str, str]]
        """
        self.__alias_name = alias_name
        self.__endpoints = endpoints

    @property
    def alias_name(self) -> typing.Optional[str]:
        return self.__alias_name

    @property
    def endpoints(self) -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]: # noqa TAE002
        return self.__endpoints
