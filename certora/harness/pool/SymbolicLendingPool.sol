pragma solidity ^0.8.10;
pragma experimental ABIEncoderV2;

import {IERC20} from '../../../lib/aave-v3-core/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import {IAToken} from "../../../lib/aave-v3-core/contracts/interfaces/IAToken.sol";
import {DataTypes} from "../../../lib/aave-v3-core/contracts/protocol/libraries/types/DataTypes.sol";

contract SymbolicLendingPool {
    // an underlying asset in the pool
    IERC20 public underlyingToken;
    // the aToken associated with the underlying above
    IAToken public aToken;
    // This index is used to convert the underlying token to its matching
    // AToken inside the pool, and vice versa.
    mapping (uint256 => uint256) public liquidityIndex;

    //DataTypes.ReserveData public reserveData;
    // Workaround, since the above triggers stack too deep issue
    uint256 configurationData;

    /**
     * @dev Deposits underlying token in the Atoken's contract on behalf of the user,
            and mints Atoken on behalf of the user in return.
     * @param asset The underlying sent by the user and to which Atoken shall be minted
     * @param amount The amount of underlying token sent by the user
     * @param onBehalfOf The recipient of the minted Atokens
     * @param referralCode A unique code (unused)
     **/
    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external {
        require(asset == address(underlyingToken));
        underlyingToken.transferFrom(
            msg.sender,
            address(aToken),
            amount
        );
        aToken.mint(
            msg.sender,
            onBehalfOf,
            amount,
            liquidityIndex[block.timestamp]
        );
    }

    /**
     * @dev Burns Atokens in exchange for underlying asset
     * @param asset The underlying asset to which the Atoken is connected
     * @param amount The amount of underlying tokens to be burned
     * @param to The recipient of the burned Atokens
     * @return The `amount` of tokens withdrawn
     **/
    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external returns (uint256) {
        require(asset == address(underlyingToken));
        aToken.burn(
            msg.sender,
            to,
            amount,
            liquidityIndex[block.timestamp]
        );
        return amount;
    }

    /**
     * @dev A simplification returning a constant
     * @param asset The underlying asset to which the Atoken is connected
     * @return liquidityIndex the `liquidityIndex` of the asset
     **/
    function getReserveNormalizedIncome(address asset)
        external
        view
        virtual
        returns (uint256)
    {
        return liquidityIndex[block.timestamp];
    }

    function reserveIsActive()
        external
        view
        returns(bool)
    {
        return (configurationData & (1  << 56) != 0);
    }

    function reserveIsFrozen()
        external
        view
        returns(bool)
    {
        return (configurationData & (1  << 57) != 0);
    }

    function assetIsPaused()
        external
        view
        returns(bool)
    {
        return (configurationData & (1  << 60) != 0);
    }

    function getReserveData(address)
        external
        view

        returns(DataTypes.ReserveData memory r)
    {
        r.configuration.data = configurationData;
        r.aTokenAddress = address(aToken);
        return r;
    }

    function getATokenAddress()
        external
        view
        returns(address)
    {
        return address(aToken);
    }
}