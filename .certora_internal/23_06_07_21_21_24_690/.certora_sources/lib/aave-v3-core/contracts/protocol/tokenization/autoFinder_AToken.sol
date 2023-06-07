// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import {IERC20} from '../../dependencies/openzeppelin/contracts/IERC20.sol';
import { GPv2SafeERC20 } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/dependencies/gnosis/contracts/autoFinder_GPv2SafeERC20.sol';
import { SafeCast } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/dependencies/openzeppelin/contracts/autoFinder_SafeCast.sol';
import { VersionedInitializable } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/protocol/libraries/aave-upgradeability/autoFinder_VersionedInitializable.sol';
import {Errors} from '../libraries/helpers/Errors.sol';
import { WadRayMath } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/protocol/libraries/math/autoFinder_WadRayMath.sol';
import {IPool} from '../../interfaces/IPool.sol';
import {IAToken} from '../../interfaces/IAToken.sol';
import {IAaveIncentivesController} from '../../interfaces/IAaveIncentivesController.sol';
import {IInitializableAToken} from '../../interfaces/IInitializableAToken.sol';
import { ScaledBalanceTokenBase } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/protocol/tokenization/base/autoFinder_ScaledBalanceTokenBase.sol';
import { IncentivizedERC20 } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/protocol/tokenization/base/autoFinder_IncentivizedERC20.sol';
import { EIP712Base } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_21_24_690/.certora_sources/lib/aave-v3-core/contracts/protocol/tokenization/base/autoFinder_EIP712Base.sol';

/**
 * @title Aave ERC20 AToken
 * @author Aave
 * @notice Implementation of the interest bearing token for the Aave protocol
 */
contract AToken is VersionedInitializable, ScaledBalanceTokenBase, EIP712Base, IAToken {
  using WadRayMath for uint256;
  using SafeCast for uint256;
  using GPv2SafeERC20 for IERC20;

  bytes32 public constant PERMIT_TYPEHASH =
    keccak256('Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)');

  uint256 public constant ATOKEN_REVISION = 0x1;

  address internal _treasury;
  address internal _underlyingAsset;

  /// @inheritdoc VersionedInitializable
  function getRevision() internal pure virtual override returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00f90000, 1037618708729) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00f90001, 0) }
    return ATOKEN_REVISION;
  }

  /**
   * @dev Constructor.
   * @param pool The address of the Pool contract
   */
  constructor(IPool pool)
    ScaledBalanceTokenBase(pool, 'ATOKEN_IMPL', 'ATOKEN_IMPL', 0)
    EIP712Base()
  {
    // Intentionally left blank
  }

  /// @inheritdoc IInitializableAToken
  function initialize(
    IPool initializingPool,
    address treasury,
    address underlyingAsset,
    IAaveIncentivesController incentivesController,
    uint8 aTokenDecimals,
    string calldata aTokenName,
    string calldata aTokenSymbol,
    bytes calldata params
  ) public virtual override logInternal263(params)initializer {
    require(initializingPool == POOL, Errors.POOL_ADDRESSES_DO_NOT_MATCH);
    _setName(aTokenName);
    _setSymbol(aTokenSymbol);
    _setDecimals(aTokenDecimals);

    _treasury = treasury;
    _underlyingAsset = underlyingAsset;
    _incentivesController = incentivesController;

    _domainSeparator = _calculateDomainSeparator();

    // commented out by certora to resolve error at analysis stage
    /*
    emit Initialized(
      underlyingAsset,
      address(POOL),
      treasury,
      address(incentivesController),
      aTokenDecimals,
      aTokenName,
      aTokenSymbol,
      params
    );
    */
  }modifier logInternal263(bytes calldata params) { assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01070000, 1037618708743) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01070001, 11) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01070003, 1400558) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01076109, params.offset) } _; }

  /// @inheritdoc IAToken
  function mint(
    address caller,
    address onBehalfOf,
    uint256 amount,
    uint256 index
  ) external virtual override onlyPool returns (bool) {
    return _mintScaled(caller, onBehalfOf, amount, index);
  }

  /// @inheritdoc IAToken
  function burn(
    address from,
    address receiverOfUnderlying,
    uint256 amount,
    uint256 index
  ) external virtual override onlyPool {
    _burnScaled(from, receiverOfUnderlying, amount, index);
    if (receiverOfUnderlying != address(this)) {
      IERC20(_underlyingAsset).safeTransfer(receiverOfUnderlying, amount);
    }
  }

  /// @inheritdoc IAToken
  function mintToTreasury(uint256 amount, uint256 index) external virtual override onlyPool {
    if (amount == 0) {
      return;
    }
    _mintScaled(address(POOL), _treasury, amount, index);
  }

  /// @inheritdoc IAToken
  function transferOnLiquidation(
    address from,
    address to,
    uint256 value
  ) external virtual override onlyPool {
    // Being a normal transfer, the Transfer() and BalanceTransfer() are emitted
    // so no need to emit a specific event here
    _transfer(from, to, value, false);
  }

  /// @inheritdoc IERC20
  function balanceOf(address user)
    public
    view
    virtual
    override(IncentivizedERC20, IERC20)
    returns (uint256)
  {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010c0000, 1037618708748) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010c0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010c1000, user) }
    return super.balanceOf(user).rayMul(POOL.getReserveNormalizedIncome(_underlyingAsset));
  }

  /// @inheritdoc IERC20
  function totalSupply() public view virtual override(IncentivizedERC20, IERC20) returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01090000, 1037618708745) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01090001, 0) }
    uint256 currentSupplyScaled = super.totalSupply();

    if (currentSupplyScaled == 0) {
      return 0;
    }

    return currentSupplyScaled.rayMul(POOL.getReserveNormalizedIncome(_underlyingAsset));
  }

  /// @inheritdoc IAToken
  function RESERVE_TREASURY_ADDRESS() external view override returns (address) {
    return _treasury;
  }

  /// @inheritdoc IAToken
  function UNDERLYING_ASSET_ADDRESS() external view override returns (address) {
    return _underlyingAsset;
  }

  /// @inheritdoc IAToken
  function transferUnderlyingTo(address target, uint256 amount) external virtual override onlyPool {
    IERC20(_underlyingAsset).safeTransfer(target, amount);
  }

  /// @inheritdoc IAToken
  function handleRepayment(
    address user,
    address onBehalfOf,
    uint256 amount
  ) external virtual override onlyPool {
    // Intentionally left blank
  }

  /// @inheritdoc IAToken
  function permit(
    address owner,
    address spender,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
  ) external override {
    require(owner != address(0), Errors.ZERO_ADDRESS_NOT_VALID);
    //solium-disable-next-line
    require(block.timestamp <= deadline, Errors.INVALID_EXPIRATION);
    uint256 currentValidNonce = _nonces[owner];
    bytes32 digest = keccak256(
      abi.encodePacked(
        '\x19\x01',
        DOMAIN_SEPARATOR(),
        keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, currentValidNonce, deadline))
      )
    );
    require(owner == ecrecover(digest, v, r, s), Errors.INVALID_SIGNATURE);
    _nonces[owner] = currentValidNonce + 1;
    _approve(owner, spender, value);
  }

  /**
   * @notice Transfers the aTokens between two users. Validates the transfer
   * (ie checks for valid HF after the transfer) if required
   * @param from The source address
   * @param to The destination address
   * @param amount The amount getting transferred
   * @param validate True if the transfer needs to be validated, false otherwise
   */
  function _transfer(
    address from,
    address to,
    uint256 amount,
    bool validate
  ) internal virtual {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa0000, 1037618708730) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa0001, 4) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa1000, from) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa1001, to) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa1002, amount) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fa1003, validate) }
    address underlyingAsset = _underlyingAsset;

    uint256 index = POOL.getReserveNormalizedIncome(underlyingAsset);

    uint256 fromBalanceBefore = super.balanceOf(from).rayMul(index);
    uint256 toBalanceBefore = super.balanceOf(to).rayMul(index);

    super._transfer(from, to, amount, index);

    if (validate) {
      POOL.finalizeTransfer(underlyingAsset, from, to, amount, fromBalanceBefore, toBalanceBefore);
    }

    emit BalanceTransfer(from, to, amount.rayDiv(index), index);
  }

  /**
   * @notice Overrides the parent _transfer to force validated transfer() and transferFrom()
   * @param from The source address
   * @param to The destination address
   * @param amount The amount getting transferred
   */
  function _transfer(
    address from,
    address to,
    uint128 amount
  ) internal virtual override {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fc0000, 1037618708732) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fc0001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fc1000, from) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fc1001, to) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fc1002, amount) }
    _transfer(from, to, amount, true);
  }

  /**
   * @dev Overrides the base function to fully implement IAToken
   * @dev see `EIP712Base.DOMAIN_SEPARATOR()` for more detailed documentation
   */
  function DOMAIN_SEPARATOR() public view override(IAToken, EIP712Base) returns (bytes32) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01080000, 1037618708744) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01080001, 0) }
    return super.DOMAIN_SEPARATOR();
  }

  /**
   * @dev Overrides the base function to fully implement IAToken
   * @dev see `EIP712Base.nonces()` for more detailed documentation
   */
  function nonces(address owner) public view override(IAToken, EIP712Base) returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010b0000, 1037618708747) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010b0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff010b1000, owner) }
    return super.nonces(owner);
  }

  /// @inheritdoc EIP712Base
  function _EIP712BaseId() internal view override returns (string memory) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fd0000, 1037618708733) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00fd0001, 0) }
    return name();
  }

  /// @inheritdoc IAToken
  function rescueTokens(
    address token,
    address to,
    uint256 amount
  ) external override onlyPoolAdmin {
    require(token != _underlyingAsset, Errors.UNDERLYING_CANNOT_BE_RESCUED);
    IERC20(token).safeTransfer(to, amount);
  }
}
