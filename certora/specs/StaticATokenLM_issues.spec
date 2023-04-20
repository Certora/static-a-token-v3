import "methods_base.spec"

/////////////////// Methods ////////////////////////

    methods
    {   
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET
        getIncentivesController() returns (address) => CONSTANT
        getRewardsList() returns (address[]) => NONDET
        //call by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
        handleAction(address,uint256,uint256) => DISPATCHER(true)
    }

////////////////// FUNCTIONS //////////////////////

    /// @title Reward hook
    /// @notice allows a single reward
    //todo: allow 2 or 3 rewards
    hook Sload address reward _rewardTokens[INDEX  uint256 i] STORAGE {
        require reward == _DummyERC20_rewardToken;
    } 

    /// @title Sum of balances of StaticAToken 
    ghost sumAllBalance() returns mathint {
        init_state axiom sumAllBalance() == 0;
    }

    hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
    havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
    }

///////////////// Properties ///////////////////////

