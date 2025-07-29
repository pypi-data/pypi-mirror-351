r'''
# `provider`

Refer to the Terraform Registry for docs: [`dnsimple`](https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DnsimpleProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-dnsimple.provider.DnsimpleProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs dnsimple}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        prefetch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sandbox: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
        user_agent: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs dnsimple} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account: The account for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#account DnsimpleProvider#account}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#alias DnsimpleProvider#alias}
        :param prefetch: Flag to enable the prefetch of zone records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#prefetch DnsimpleProvider#prefetch}
        :param sandbox: Flag to enable the sandbox API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#sandbox DnsimpleProvider#sandbox}
        :param token: The API v2 token for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#token DnsimpleProvider#token}
        :param user_agent: Custom string to append to the user agent used for sending HTTP requests to the API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#user_agent DnsimpleProvider#user_agent}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7ef56b7728822c45a23750e2602fff787208bfb71fa54a96467397e10a6e47c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DnsimpleProviderConfig(
            account=account,
            alias=alias,
            prefetch=prefetch,
            sandbox=sandbox,
            token=token,
            user_agent=user_agent,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DnsimpleProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DnsimpleProvider to import.
        :param import_from_id: The id of the existing DnsimpleProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DnsimpleProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4edfc9e8a657653d4fcd97200d4c0bf459f5954ee5b33da4ca414163f4b238e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetPrefetch")
    def reset_prefetch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefetch", []))

    @jsii.member(jsii_name="resetSandbox")
    def reset_sandbox(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSandbox", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetUserAgent")
    def reset_user_agent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserAgent", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="accountInput")
    def account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="prefetchInput")
    def prefetch_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "prefetchInput"))

    @builtins.property
    @jsii.member(jsii_name="sandboxInput")
    def sandbox_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sandboxInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="userAgentInput")
    def user_agent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgentInput"))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "account"))

    @account.setter
    def account(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be9c643fcd01fe5cf275169fcc97ae0d00374eb3d20c7266c6169c4c5dcb3d1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "account", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7934afbef683b54bd8d5d4af05f10bf12679fa0e659fb0f4faa41ea7619c9b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefetch")
    def prefetch(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "prefetch"))

    @prefetch.setter
    def prefetch(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bf197dbff924b955b511e222428391ca41e320c43ae7cee266e74ceeed0d9ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefetch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sandbox")
    def sandbox(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sandbox"))

    @sandbox.setter
    def sandbox(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf21cfd11d99d30d47061d43f7c389e5f8726eb7ac49328f36121a633625bcae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sandbox", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49665df0ea9a243b8910eb1a9d0d5446caf446fc87e8d9fb45c4b311129a2a16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userAgent")
    def user_agent(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgent"))

    @user_agent.setter
    def user_agent(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6463b0002aeec81758c6a086bf480d9e4729e0a16b2609cfbb08883d426780)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userAgent", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-dnsimple.provider.DnsimpleProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "alias": "alias",
        "prefetch": "prefetch",
        "sandbox": "sandbox",
        "token": "token",
        "user_agent": "userAgent",
    },
)
class DnsimpleProviderConfig:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        prefetch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sandbox: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
        user_agent: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: The account for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#account DnsimpleProvider#account}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#alias DnsimpleProvider#alias}
        :param prefetch: Flag to enable the prefetch of zone records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#prefetch DnsimpleProvider#prefetch}
        :param sandbox: Flag to enable the sandbox API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#sandbox DnsimpleProvider#sandbox}
        :param token: The API v2 token for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#token DnsimpleProvider#token}
        :param user_agent: Custom string to append to the user agent used for sending HTTP requests to the API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#user_agent DnsimpleProvider#user_agent}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38b8bc1cdf1e0a8d7a730ac02381391ddfa090074fe8470d004c65b043c59d30)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument prefetch", value=prefetch, expected_type=type_hints["prefetch"])
            check_type(argname="argument sandbox", value=sandbox, expected_type=type_hints["sandbox"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument user_agent", value=user_agent, expected_type=type_hints["user_agent"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if alias is not None:
            self._values["alias"] = alias
        if prefetch is not None:
            self._values["prefetch"] = prefetch
        if sandbox is not None:
            self._values["sandbox"] = sandbox
        if token is not None:
            self._values["token"] = token
        if user_agent is not None:
            self._values["user_agent"] = user_agent

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The account for API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#account DnsimpleProvider#account}
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#alias DnsimpleProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefetch(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to enable the prefetch of zone records.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#prefetch DnsimpleProvider#prefetch}
        '''
        result = self._values.get("prefetch")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sandbox(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to enable the sandbox API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#sandbox DnsimpleProvider#sandbox}
        '''
        result = self._values.get("sandbox")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The API v2 token for API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#token DnsimpleProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_agent(self) -> typing.Optional[builtins.str]:
        '''Custom string to append to the user agent used for sending HTTP requests to the API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/dnsimple/dnsimple/1.9.1/docs#user_agent DnsimpleProvider#user_agent}
        '''
        result = self._values.get("user_agent")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsimpleProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DnsimpleProvider",
    "DnsimpleProviderConfig",
]

publication.publish()

def _typecheckingstub__e7ef56b7728822c45a23750e2602fff787208bfb71fa54a96467397e10a6e47c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    prefetch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sandbox: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
    user_agent: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4edfc9e8a657653d4fcd97200d4c0bf459f5954ee5b33da4ca414163f4b238e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9c643fcd01fe5cf275169fcc97ae0d00374eb3d20c7266c6169c4c5dcb3d1a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7934afbef683b54bd8d5d4af05f10bf12679fa0e659fb0f4faa41ea7619c9b3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf197dbff924b955b511e222428391ca41e320c43ae7cee266e74ceeed0d9ca(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf21cfd11d99d30d47061d43f7c389e5f8726eb7ac49328f36121a633625bcae(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49665df0ea9a243b8910eb1a9d0d5446caf446fc87e8d9fb45c4b311129a2a16(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6463b0002aeec81758c6a086bf480d9e4729e0a16b2609cfbb08883d426780(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b8bc1cdf1e0a8d7a730ac02381391ddfa090074fe8470d004c65b043c59d30(
    *,
    account: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    prefetch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sandbox: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
    user_agent: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
