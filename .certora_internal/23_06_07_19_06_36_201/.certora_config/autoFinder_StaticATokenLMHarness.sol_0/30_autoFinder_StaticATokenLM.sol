// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {IPool} from 'aave-v3-core/contracts/interfaces/IPool.sol';
import { DataTypes, ReserveConfiguration } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/aave-v3-core/contracts/protocol/libraries/configuration/autoFinder_ReserveConfiguration.sol';
import {IScaledBalanceToken} from 'aave-v3-core/contracts/interfaces/IScaledBalanceToken.sol';
import {IRewardsController} from 'aave-v3-periphery/contracts/rewards/interfaces/IRewardsController.sol';
import { WadRayMath } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/aave-v3-core/contracts/protocol/libraries/math/autoFinder_WadRayMath.sol';
import { MathUtils } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/aave-v3-core/contracts/protocol/libraries/math/autoFinder_MathUtils.sol';
import { SafeCast } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/openzeppelin-contracts/contracts/utils/math/autoFinder_SafeCast.sol';
import { Initializable } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/solidity-utils/src/contracts/transparent-proxy/autoFinder_Initializable.sol';
import { SafeERC20 } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/lib/solidity-utils/src/contracts/oz-common/autoFinder_SafeERC20.sol';
import {IERC20Metadata} from 'solidity-utils/contracts/oz-common/interfaces/IERC20Metadata.sol';
import {IERC20} from 'solidity-utils/contracts/oz-common/interfaces/IERC20.sol';
import {IERC20WithPermit} from 'solidity-utils/contracts/oz-common/interfaces/IERC20WithPermit.sol';

import {IStaticATokenLM} from './interfaces/IStaticATokenLM.sol';
import {IAToken} from './interfaces/IAToken.sol';
import { ERC20 } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/src/autoFinder_ERC20.sol';
import {IInitializableStaticATokenLM} from './interfaces/IInitializableStaticATokenLM.sol';
import {StaticATokenErrors} from './StaticATokenErrors.sol';
import { RayMathExplicitRounding, Rounding } from '/home/dev1644/workspace/workspace-test/aave-certora/.certora_internal/23_06_07_19_06_36_201/.certora_sources/src/autoFinder_RayMathExplicitRounding.sol';
import {IERC4626} from './interfaces/IERC4626.sol';

/**
 * @title StaticATokenLM
 * @notice Wrapper smart contract that allows to deposit tokens on the Aave protocol and receive
 * a token which balance doesn't increase automatically, but uses an ever-increasing exchange rate.
 * It supports claiming liquidity mining rewards from the Aave system.
 * @author BGD labs
 */
contract StaticATokenLM is
  Initializable,
  ERC20('STATIC__aToken_IMPL', 'STATIC__aToken_IMPL', 18),
  IStaticATokenLM,
  IERC4626
{
  using SafeERC20 for IERC20;
  using SafeCast for uint256;
  using WadRayMath for uint256;
  using RayMathExplicitRounding for uint256;

  bytes32 public constant METADEPOSIT_TYPEHASH =
    keccak256(
      'Deposit(address depositor,address recipient,uint256 value,uint16 referralCode,bool fromUnderlying,uint256 nonce,uint256 deadline,PermitParams permit)'
    );
  bytes32 public constant METAWITHDRAWAL_TYPEHASH =
    keccak256(
      'Withdraw(address owner,address recipient,uint256 staticAmount,uint256 dynamicAmount,bool toUnderlying,uint256 nonce,uint256 deadline)'
    );

  uint256 public constant STATIC__ATOKEN_LM_REVISION = 1;

  IPool public immutable POOL;
  IRewardsController public immutable INCENTIVES_CONTROLLER;

  IERC20 internal _aToken;
  address internal _aTokenUnderlying;
  address[] internal _rewardTokens;
  mapping(address => RewardIndexCache) internal _startIndex;
  mapping(address => mapping(address => UserRewardsData)) internal _userRewardsData;

  constructor(IPool pool, IRewardsController rewardsController) {
    POOL = pool;
    INCENTIVES_CONTROLLER = rewardsController;
  }

  ///@inheritdoc IInitializableStaticATokenLM
  function initialize(
    address newAToken,
    string calldata staticATokenName,
    string calldata staticATokenSymbol
  ) external initializer {
    _aToken = IERC20(newAToken);

    name = staticATokenName;
    symbol = staticATokenSymbol;
    decimals = IERC20Metadata(newAToken).decimals();

    _aTokenUnderlying = IAToken(newAToken).UNDERLYING_ASSET_ADDRESS();
    IERC20(_aTokenUnderlying).safeApprove(address(POOL), type(uint256).max);

    if (INCENTIVES_CONTROLLER != IRewardsController(address(0))) {
      refreshRewardTokens();
    }

    emit Initialized(newAToken, staticATokenName, staticATokenSymbol);
  }

  ///@inheritdoc IStaticATokenLM
  function refreshRewardTokens() public override {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff000f0000, 1037618708495) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff000f0001, 0) }
    address[] memory rewards = INCENTIVES_CONTROLLER.getRewardsByAsset(address(_aToken));
    for (uint256 i = 0; i < rewards.length; i++) {
      _registerRewardToken(rewards[i]);
    }
  }

  ///@inheritdoc IStaticATokenLM
  function isRegisteredRewardToken(address reward) public view override returns (bool) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00140000, 1037618708500) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00140001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00141000, reward) }
    return _startIndex[reward].isRegistered;
  }

  ///@inheritdoc IStaticATokenLM
  function deposit(
    uint256 assets,
    address recipient,
    uint16 referralCode,
    bool fromUnderlying
  ) external returns (uint256) {
    return _deposit(msg.sender, recipient, assets, referralCode, fromUnderlying);
  }

  ///@inheritdoc IStaticATokenLM
  function metaDeposit(
    address depositor,
    address recipient,
    uint256 value,
    uint16 referralCode,
    bool fromUnderlying,
    uint256 deadline,
    PermitParams calldata permit,
    SignatureParams calldata sigParams
  ) external returns (uint256) {
    require(depositor != address(0), StaticATokenErrors.INVALID_DEPOSITOR);
    //solium-disable-next-line
    require(deadline >= block.timestamp, StaticATokenErrors.INVALID_EXPIRATION);
    uint256 nonce = nonces[depositor];

    // Unchecked because the only math done is incrementing
    // the owner's nonce which cannot realistically overflow.
    unchecked {
      bytes32 digest = keccak256(
        abi.encodePacked(
          '\x19\x01',
          DOMAIN_SEPARATOR(),
          keccak256(
            abi.encode(
              METADEPOSIT_TYPEHASH,
              depositor,
              recipient,
              value,
              referralCode,
              fromUnderlying,
              nonce,
              deadline,
              permit
            )
          )
        )
      );
      nonces[depositor] = nonce + 1;
      require(
        depositor == ecrecover(digest, sigParams.v, sigParams.r, sigParams.s),
        StaticATokenErrors.INVALID_SIGNATURE
      );
    }
    // assume if deadline 0 no permit was supplied
    if (permit.deadline != 0) {
      IERC20WithPermit(fromUnderlying ? address(_aTokenUnderlying) : address(_aToken)).permit(
        depositor,
        address(this),
        permit.value,
        permit.deadline,
        permit.v,
        permit.r,
        permit.s
      );
    }
    return _deposit(depositor, recipient, value, referralCode, fromUnderlying);
  }

  ///@inheritdoc IStaticATokenLM
  function metaWithdraw(
    address owner,
    address recipient,
    uint256 staticAmount,
    uint256 dynamicAmount,
    bool toUnderlying,
    uint256 deadline,
    SignatureParams calldata sigParams
  ) external returns (uint256, uint256) {
    require(owner != address(0), StaticATokenErrors.INVALID_OWNER);
    //solium-disable-next-line
    require(deadline >= block.timestamp, StaticATokenErrors.INVALID_EXPIRATION);
    uint256 nonce = nonces[owner];
    // Unchecked because the only math done is incrementing
    // the owner's nonce which cannot realistically overflow.
    unchecked {
      bytes32 digest = keccak256(
        abi.encodePacked(
          '\x19\x01',
          DOMAIN_SEPARATOR(),
          keccak256(
            abi.encode(
              METAWITHDRAWAL_TYPEHASH,
              owner,
              recipient,
              staticAmount,
              dynamicAmount,
              toUnderlying,
              nonce,
              deadline
            )
          )
        )
      );
      nonces[owner] = nonce + 1;
      require(
        owner == ecrecover(digest, sigParams.v, sigParams.r, sigParams.s),
        StaticATokenErrors.INVALID_SIGNATURE
      );
    }
    return _withdraw(owner, recipient, staticAmount, dynamicAmount, toUnderlying);
  }

  ///@inheritdoc IERC4626
  function previewRedeem(uint256 shares) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001d0000, 1037618708509) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001d0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001d1000, shares) }
    return _convertToAssets(shares, Rounding.DOWN);
  }

  ///@inheritdoc IERC4626
  function previewMint(uint256 shares) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001a0000, 1037618708506) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001a0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001a1000, shares) }
    return _convertToAssets(shares, Rounding.UP);
  }

  ///@inheritdoc IERC4626
  function previewWithdraw(uint256 assets) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001c0000, 1037618708508) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001c0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001c1000, assets) }
    return _convertToShares(assets, Rounding.UP);
  }

  ///@inheritdoc IERC4626
  function previewDeposit(uint256 assets) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00250000, 1037618708517) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00250001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00251000, assets) }
    return _convertToShares(assets, Rounding.DOWN);
  }

  ///@inheritdoc IStaticATokenLM
  function rate() public view returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00160000, 1037618708502) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00160001, 0) }
    return POOL.getReserveNormalizedIncome(_aTokenUnderlying);
  }

  ///@inheritdoc IStaticATokenLM
  function collectAndUpdateRewards(address reward) public returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001e0000, 1037618708510) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001e0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001e1000, reward) }
    if (reward == address(0)) {
      return 0;
    }

    address[] memory assets = new address[](1);
    assets[0] = address(_aToken);

    return INCENTIVES_CONTROLLER.claimRewards(assets, type(uint256).max, address(this), reward);
  }

  ///@inheritdoc IStaticATokenLM
  function claimRewardsOnBehalf(
    address onBehalfOf,
    address receiver,
    address[] memory rewards
  ) external {
    require(
      msg.sender == onBehalfOf || msg.sender == INCENTIVES_CONTROLLER.getClaimer(onBehalfOf),
      StaticATokenErrors.INVALID_CLAIMER
    );
    _claimRewardsOnBehalf(onBehalfOf, receiver, rewards);
  }

  ///@inheritdoc IStaticATokenLM
  function claimRewards(address receiver, address[] memory rewards) external {
    _claimRewardsOnBehalf(msg.sender, receiver, rewards);
  }

  ///@inheritdoc IStaticATokenLM
  function claimRewardsToSelf(address[] memory rewards) external {
    _claimRewardsOnBehalf(msg.sender, msg.sender, rewards);
  }

  ///@inheritdoc IStaticATokenLM
  function getCurrentRewardsIndex(address reward) public view returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00130000, 1037618708499) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00130001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00131000, reward) }
    if (address(reward) == address(0)) {
      return 0;
    }
    (, uint256 nextIndex) = INCENTIVES_CONTROLLER.getAssetIndex(address(_aToken), reward);
    return nextIndex;
  }

  ///@inheritdoc IStaticATokenLM
  function getTotalClaimableRewards(address reward) external view returns (uint256) {
    if (reward == address(0)) {
      return 0;
    }

    address[] memory assets = new address[](1);
    assets[0] = address(_aToken);
    uint256 freshRewards = INCENTIVES_CONTROLLER.getUserRewards(assets, address(this), reward);
    return IERC20(reward).balanceOf(address(this)) + freshRewards;
  }

  ///@inheritdoc IStaticATokenLM
  function getClaimableRewards(address user, address reward) external view returns (uint256) {
    return _getClaimableRewards(user, reward, balanceOf[user], getCurrentRewardsIndex(reward));
  }

  ///@inheritdoc IStaticATokenLM
  function getUnclaimedRewards(address user, address reward) external view returns (uint256) {
    return _userRewardsData[user][reward].unclaimedRewards;
  }

  ///@inheritdoc IERC4626
  function asset() external view returns (address) {
    return address(_aToken);
  }

  ///@inheritdoc IStaticATokenLM
  function aToken() external view returns (IERC20) {
    return _aToken;
  }

  ///@inheritdoc IStaticATokenLM
  function aTokenUnderlying() external view returns (IERC20) {
    return IERC20(_aTokenUnderlying);
  }

  ///@inheritdoc IStaticATokenLM
  function rewardTokens() external view returns (address[] memory) {
    return _rewardTokens;
  }

  ///@inheritdoc IERC4626
  function totalAssets() external view returns (uint256) {
    return _aToken.balanceOf(address(this));
  }

  ///@inheritdoc IERC4626
  function convertToShares(uint256 amount) external view returns (uint256) {
    return _convertToShares(amount, Rounding.DOWN);
  }

  ///@inheritdoc IERC4626
  function convertToAssets(uint256 shares) external view returns (uint256) {
    return _convertToAssets(shares, Rounding.DOWN);
  }

  ///@inheritdoc IERC4626
  function maxDeposit(address) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00260000, 1037618708518) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00260001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00265000, 0) }
    return type(uint256).max;
  }

  ///@inheritdoc IERC4626
  function maxMint(address) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00190000, 1037618708505) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00190001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00195000, 0) }
    return type(uint256).max;
  }

  ///@inheritdoc IERC4626
  function maxWithdraw(address owner) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00170000, 1037618708503) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00170001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00171000, owner) }
    return _convertToAssets(balanceOf[owner], Rounding.DOWN);
  }

  ///@inheritdoc IERC4626
  function maxRedeem(address owner) public view virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00270000, 1037618708519) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00270001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00271000, owner) }
    return balanceOf[owner];
  }

  ///@inheritdoc IStaticATokenLM
  function maxRedeemUnderlying(address owner) external view virtual returns (uint256) {
    address cachedATokenUnderlying = _aTokenUnderlying;
    DataTypes.ReserveData memory reserveData = POOL.getReserveData(cachedATokenUnderlying);

    // if paused or inactive users cannot withraw underlying
    if (
      !ReserveConfiguration.getActive(reserveData.configuration) ||
      ReserveConfiguration.getPaused(reserveData.configuration)
    ) {
      return 0;
    }

    // otherwise users can withdraw up to the available amount
    uint256 underlyingTokenBalanceInShares = _convertToShares(
      IERC20(cachedATokenUnderlying).balanceOf(reserveData.aTokenAddress),
      Rounding.DOWN
    );
    uint256 cachedUserBalance = balanceOf[owner];
    return
      underlyingTokenBalanceInShares >= cachedUserBalance
        ? cachedUserBalance
        : underlyingTokenBalanceInShares;
  }

  ///@inheritdoc IStaticATokenLM
  function maxDepositUnderlying(address) external view virtual returns (uint256) {
    DataTypes.ReserveData memory reserveData = POOL.getReserveData(_aTokenUnderlying);

    // if inactive, paused or frozen users cannot deposit underlying
    if (
      !ReserveConfiguration.getActive(reserveData.configuration) ||
      ReserveConfiguration.getPaused(reserveData.configuration) ||
      ReserveConfiguration.getFrozen(reserveData.configuration)
    ) {
      return 0;
    }

    uint256 supplyCap = ReserveConfiguration.getSupplyCap(reserveData.configuration) *
      (10 ** ReserveConfiguration.getDecimals(reserveData.configuration));
    // if no supply cap deposit is unlimited
    if (supplyCap == 0) return type(uint256).max;
    // return remaining supply cap margin
    uint256 currentSupply = (IAToken(reserveData.aTokenAddress).scaledTotalSupply() +
      reserveData.accruedToTreasury).rayMulRoundUp(_getNormalizedIncome(reserveData));
    return currentSupply > supplyCap ? 0 : supplyCap - currentSupply;
  }

  ///@inheritdoc IERC4626
  function deposit(uint256 assets, address receiver) public virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00230000, 1037618708515) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00230001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00231000, assets) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00231001, receiver) }
    return _deposit(msg.sender, receiver, assets, 0, false);
  }

  ///@inheritdoc IERC4626
  function mint(uint256 shares, address receiver) public virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001f0000, 1037618708511) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001f0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001f1000, shares) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff001f1001, receiver) }
    require(shares != 0, StaticATokenErrors.INVALID_ZERO_AMOUNT);
    require(shares <= maxMint(receiver), 'ERC4626: mint more than max');

    uint256 assets = previewMint(shares);
    _deposit(msg.sender, receiver, assets, 0, false);

    return assets;
  }

  ///@inheritdoc IERC4626
  function withdraw(
    uint256 assets,
    address receiver,
    address owner
  ) public virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00100000, 1037618708496) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00100001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00101000, assets) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00101001, receiver) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00101002, owner) }
    require(assets <= maxWithdraw(owner), 'ERC4626: withdraw more than max');

    (uint256 shares, ) = _withdraw(owner, receiver, 0, assets, false);

    return shares;
  }

  ///@inheritdoc IERC4626
  function redeem(
    uint256 shares,
    address receiver,
    address owner
  ) public virtual returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00210000, 1037618708513) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00210001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00211000, shares) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00211001, receiver) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00211002, owner) }
    require(shares <= maxRedeem(owner), 'ERC4626: redeem more than max');

    (, uint256 assets) = _withdraw(owner, receiver, shares, 0, false);

    return assets;
  }

  ///@inheritdoc IStaticATokenLM
  function redeem(
    uint256 shares,
    address receiver,
    address owner,
    bool toUnderlying
  ) public virtual returns (uint256, uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00110000, 1037618708497) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00110001, 4) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00111000, shares) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00111001, receiver) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00111002, owner) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00111003, toUnderlying) }
    require(shares <= maxRedeem(owner), 'ERC4626: redeem more than max');

    return _withdraw(owner, receiver, shares, 0, toUnderlying);
  }

  function _deposit(
    address depositor,
    address recipient,
    uint256 assets,
    uint16 referralCode,
    bool fromUnderlying
  ) internal returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00000000, 1037618708480) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00000001, 5) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00001000, depositor) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00001001, recipient) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00001002, assets) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00001003, referralCode) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00001004, fromUnderlying) }
    require(recipient != address(0), StaticATokenErrors.INVALID_RECIPIENT);
    uint256 shares = previewDeposit(assets);
    require(shares != 0, StaticATokenErrors.INVALID_ZERO_AMOUNT);

    if (fromUnderlying) {
      address cachedATokenUnderlying = _aTokenUnderlying;
      IERC20(cachedATokenUnderlying).safeTransferFrom(depositor, address(this), assets);
      POOL.deposit(cachedATokenUnderlying, assets, address(this), referralCode);
    } else {
      _aToken.safeTransferFrom(depositor, address(this), assets);
    }

    _mint(recipient, shares);

    emit Deposit(msg.sender, recipient, assets, shares);

    return shares;
  }

  function _withdraw(
    address owner,
    address recipient,
    uint256 staticAmount,
    uint256 dynamicAmount,
    bool toUnderlying
  ) internal returns (uint256, uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00010000, 1037618708481) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00010001, 5) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00011000, owner) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00011001, recipient) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00011002, staticAmount) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00011003, dynamicAmount) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00011004, toUnderlying) }
    require(recipient != address(0), StaticATokenErrors.INVALID_RECIPIENT);
    require(
      staticAmount == 0 || dynamicAmount == 0,
      StaticATokenErrors.ONLY_ONE_AMOUNT_FORMAT_ALLOWED
    );
    require(staticAmount != dynamicAmount, StaticATokenErrors.INVALID_ZERO_AMOUNT);

    uint256 amountToWithdraw = dynamicAmount;
    uint256 shares = staticAmount;

    if (staticAmount > 0) {
      amountToWithdraw = previewRedeem(staticAmount);
    } else {
      shares = previewWithdraw(dynamicAmount);
    }

    if (msg.sender != owner) {
      uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

      if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
    }

    _burn(owner, shares);

    emit Withdraw(msg.sender, recipient, owner, amountToWithdraw, shares);

    if (toUnderlying) {
      POOL.withdraw(_aTokenUnderlying, amountToWithdraw, recipient);
    } else {
      _aToken.safeTransfer(recipient, amountToWithdraw);
    }

    return (shares, amountToWithdraw);
  }

  /**
   * @notice Updates rewards for senders and receiver in a transfer (not updating rewards for address(0))
   * @param from The address of the sender of tokens
   * @param to The address of the receiver of tokens
   * @param amount The amount of tokens to transfer in WAD
   */
  function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00030000, 1037618708483) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00030001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00031000, from) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00031001, to) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00031002, amount) }
    for (uint256 i = 0; i < _rewardTokens.length; i++) {
      address rewardToken = address(_rewardTokens[i]);
      uint256 rewardsIndex = getCurrentRewardsIndex(rewardToken);
      if (from != address(0)) {
        _updateUser(from, rewardsIndex, rewardToken);
      }
      if (to != address(0) && from != to) {
        _updateUser(to, rewardsIndex, rewardToken);
      }
    }
  }

  /**
   * @notice Adding the pending rewards to the unclaimed for specific user and updating user index
   * @param user The address of the user to update
   * @param currentRewardsIndex The current rewardIndex
   * @param rewardToken The address of the reward token
   */
  function _updateUser(address user, uint256 currentRewardsIndex, address rewardToken) internal {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00040000, 1037618708484) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00040001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00041000, user) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00041001, currentRewardsIndex) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00041002, rewardToken) }
    uint256 balance = balanceOf[user];
    if (balance > 0) {
      _userRewardsData[user][rewardToken].unclaimedRewards = _getClaimableRewards(
        user,
        rewardToken,
        balance,
        currentRewardsIndex
      ).toUint128();
    }
    _userRewardsData[user][rewardToken].rewardsIndexOnLastInteraction = currentRewardsIndex
      .toUint128();
  }

  /**
   * @notice Compute the pending in WAD. Pending is the amount to add (not yet unclaimed) rewards in WAD.
   * @param balance The balance of the user
   * @param rewardsIndexOnLastInteraction The index which was on the last interaction of the user
   * @param currentRewardsIndex The current rewards index in the system
   * @param assetUnit One unit of asset (10**decimals)
   * @return The amount of pending rewards in WAD
   */
  function _getPendingRewards(
    uint256 balance,
    uint256 rewardsIndexOnLastInteraction,
    uint256 currentRewardsIndex,
    uint256 assetUnit
  ) internal pure returns (uint256) {uint256 certoraRename2_0 = balance;assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00020000, 1037618708482) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00020001, 4) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00021000, certoraRename2_0) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00021001, rewardsIndexOnLastInteraction) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00021002, currentRewardsIndex) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00021003, assetUnit) }
    if (balance == 0) {
      return 0;
    }
    return (balance * (currentRewardsIndex - rewardsIndexOnLastInteraction)) / assetUnit;
  }

  /**
   * @notice Compute the claimable rewards for a user
   * @param user The address of the user
   * @param reward The address of the reward
   * @param balance The balance of the user in WAD
   * @return The total rewards that can be claimed by the user (if `fresh` flag true, after updating rewards)
   */
  function _getClaimableRewards(
    address user,
    address reward,
    uint256 balance,
    uint256 currentRewardsIndex
  ) internal view returns (uint256) {uint256 certoraRename5_2 = balance;assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00050000, 1037618708485) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00050001, 4) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00051000, user) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00051001, reward) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00051002, certoraRename5_2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00051003, currentRewardsIndex) }
    RewardIndexCache memory rewardsIndexCache = _startIndex[reward];
    require(rewardsIndexCache.isRegistered == true, StaticATokenErrors.REWARD_NOT_INITIALIZED);
    UserRewardsData memory currentUserRewardsData = _userRewardsData[user][reward];
    uint256 assetUnit = 10 ** decimals;
    return
      currentUserRewardsData.unclaimedRewards +
      _getPendingRewards(
        balance,
        currentUserRewardsData.rewardsIndexOnLastInteraction == 0
          ? rewardsIndexCache.lastUpdatedIndex
          : currentUserRewardsData.rewardsIndexOnLastInteraction,
        currentRewardsIndex,
        assetUnit
      );
  }

  /**
   * @notice Claim rewards on behalf of a user and send them to a receiver
   * @param onBehalfOf The address to claim on behalf of
   * @param rewards The addresses of the rewards
   * @param receiver The address to receive the rewards
   */
  function _claimRewardsOnBehalf(
    address onBehalfOf,
    address receiver,
    address[] memory rewards
  ) internal {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00060000, 1037618708486) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00060001, 3) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00061000, onBehalfOf) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00061001, receiver) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00061002, rewards) }
    for (uint256 i = 0; i < rewards.length; i++) {
      if (address(rewards[i]) == address(0)) {
        continue;
      }
      uint256 currentRewardsIndex = getCurrentRewardsIndex(rewards[i]);
      uint256 balance = balanceOf[onBehalfOf];
      uint256 userReward = _getClaimableRewards(
        onBehalfOf,
        rewards[i],
        balance,
        currentRewardsIndex
      );
      uint256 totalRewardTokenBalance = IERC20(rewards[i]).balanceOf(address(this));
      uint256 unclaimedReward = 0;

      if (userReward > totalRewardTokenBalance) {
        totalRewardTokenBalance += collectAndUpdateRewards(address(rewards[i]));
      }

      if (userReward > totalRewardTokenBalance) {
        unclaimedReward = userReward - totalRewardTokenBalance;
        userReward = totalRewardTokenBalance;
      }
      if (userReward > 0) {
        _userRewardsData[onBehalfOf][rewards[i]].unclaimedRewards = unclaimedReward.toUint128();
        _userRewardsData[onBehalfOf][rewards[i]].rewardsIndexOnLastInteraction = currentRewardsIndex
          .toUint128();
        IERC20(rewards[i]).safeTransfer(receiver, userReward);
      }
    }
  }

  function _convertToShares(uint256 amount, Rounding rounding) internal view returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00070000, 1037618708487) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00070001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00071000, amount) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00071001, rounding) }
    if (rounding == Rounding.UP) return amount.rayDivRoundUp(rate());
    return amount.rayDivRoundDown(rate());
  }

  function _convertToAssets(uint256 shares, Rounding rounding) internal view returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00080000, 1037618708488) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00080001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00081000, shares) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00081001, rounding) }
    if (rounding == Rounding.UP) return shares.rayMulRoundUp(rate());
    return shares.rayMulRoundDown(rate());
  }

  /**
   * @notice Initializes a new rewardToken
   * @param reward The reward token to be registered
   */
  function _registerRewardToken(address reward) internal {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00090000, 1037618708489) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00090001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00091000, reward) }
    if (isRegisteredRewardToken(reward)) return;
    uint256 startIndex = getCurrentRewardsIndex(reward);

    _rewardTokens.push(reward);
    _startIndex[reward] = RewardIndexCache(true, startIndex.toUint240());

    emit RewardTokenRegistered(reward, startIndex);
  }

  /**
   * Copy of https://github.com/aave/aave-v3-core/blob/29ff9b9f89af7cd8255231bc5faf26c3ce0fb7ce/contracts/protocol/libraries/logic/ReserveLogic.sol#L47 with memory instead of calldata
   * @notice Returns the ongoing normalized income for the reserve.
   * @dev A value of 1e27 means there is no income. As time passes, the income is accrued
   * @dev A value of 2*1e27 means for each unit of asset one unit of income has been accrued
   * @param reserve The reserve object
   * @return The normalized income, expressed in ray
   */
  function _getNormalizedIncome(
    DataTypes.ReserveData memory reserve
  ) internal view returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff000a0000, 1037618708490) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff000a0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff000a1000, reserve) }
    uint40 timestamp = reserve.lastUpdateTimestamp;

    //solium-disable-next-line
    if (timestamp == block.timestamp) {
      //if the index was updated in the same block, no need to perform any calculation
      return reserve.liquidityIndex;
    } else {
      return
        MathUtils.calculateLinearInterest(reserve.currentLiquidityRate, timestamp).rayMul(
          reserve.liquidityIndex
        );
    }
  }
}
