import "erc20Summarized.spec"

using StaticATokenLMHarness as SAT
using AToken as ATok
using SymbolicLendingPoolL1 as pool

/////////////////// Methods ////////////////////////

    methods{

        pool.getReserveNormalizedIncome(address) returns (uint256)
        getStaticATokenUnderlying() returns (address) envfree
        ATok._underlyingAsset() returns (address) envfree
    }

///////////////// DEFINITIONS //////////////////////

    definition RAY() returns uint256 = 10^27;

///////////////// Properties ///////////////////////

    /********************
    *      deposit      *
    *********************/

        // The deposit function does not always deposit exactly the amount of assets specified by the user during the function call due to rounding error
        // The following two rules check that the user gets an non-zero amount of shares if the specified amount of assets to be deposited is at least
        // equivalent of 1 AToken. Refer to the erc4626DepositSummarization spec for rules asserting the upper bound of the amount of assets 
        // deposited in a deposit function call

        // STATUS: Verified
        // https://vaas-stg.certora.com/output/11775/b10cd30ab6fb400baeff6b61c07bb375/?anonymousKey=ccba22e832b7549efea9f0d4b1288da2c1377ccb
        ///@title Deposit function mint amount check for index > RAY
        ///@notice This rule checks that, for index > RAY, the deposit function will mint atleast 1 share as long as the specified deposit amount is worth atleast 1 AToken 
        rule depositCheckIndexGRayAssert2(env e){
            uint256 assets;
            address receiver;
            uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
            
            require getStaticATokenUnderlying() == ATok._underlyingAsset();//Without this a different index will be used for conversions in the Atoken contract compared to the one used in StaticAToken
            require e.msg.sender != currentContract;
            require index > RAY();//since the index is initiated as RAY and only increases after that. index < RAY gives strange behaviors causing wildly inaccurate amounts being deposited and minted

            uint256 shares = deposit(e, assets, receiver);
            
            assert assets * RAY() >= index => shares != 0; //if the assets amount is worth at least 1 Atoken then receiver will get atleast 1 share
        }

        // STATUS: Verified
        // https://vaas-stg.certora.com/output/11775/2e162e12cafb49e688a7959a1d7dd4ca/?anonymousKey=d23ad1899e6bfa4e14fbf79799d008fa003dd633
        ///@title Deposit function mint amount check for index == RAY
        ///@notice This rule checks that, for index == RAY, the deposit function will mint atleast 1 share as long as the specified deposit amount is worth atleast 1 AToken

        rule depositCheckIndexERayAssert2(env e){
            uint256 assets;
            address receiver;
            uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
            
            require getStaticATokenUnderlying() == ATok._underlyingAsset();//Without this a different index will be used for conversions in the Atoken contract compared to the one used in StaticAToken
            require e.msg.sender != currentContract;
            require index == RAY();//since the index is initiated as RAY and only increases after that. index < RAY gives strange behaviors causing wildly inaccurate amounts being deposited and minted

            uint256 shares = deposit(e, assets, receiver);
            
            assert assets * RAY() >= index => shares != 0; //if the assets amount is worth at least 1 Atoken then receiver will get atleast 1 share
        }
        
    /*****************
    *      mint      *
    ******************/

        /***
        * rule to check the following for the mint function:
        * 1. MUST revert if all of shares cannot be minted
        */
        // The mint function doesn't always mint exactly the number of shares specified in the function call due to rounding off.
        // The following two rules check that the user will at least get as many shares they wanted to mint and upto one extra share
        // over the specified amount
        // STATUS: Verified
        // https://vaas-stg.certora.com/output/11775/b6f6335e770b42ffa280e40d6f82906d/?anonymousKey=ed369d98039f29134aa774592c533ec0c4a9c08e
        ///@title mint function check for upper bound of shares minted
        ///@notice This rules checks that the mint function, for index  > RAY, mints upto 1 extra share over the amount specified by the caller
        rule mintCheckIndexGRayUpperBound(env e){
            uint256 shares;
            address receiver;
            uint256 assets;
            require getStaticATokenUnderlying() == ATok._underlyingAsset();
            require e.msg.sender != currentContract;
            uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

            uint256 receiverBalBefore = balanceOf(receiver);
            require receiverBalBefore + shares <= max_uint256;//avoiding overflow
            require index > RAY();
            
            assets = mint(e, shares, receiver);
            
            uint256 receiverBalAfter = balanceOf(receiver);
            // upperbound
            assert receiverBalAfter <= receiverBalBefore + shares + 1,"receiver should get no more than the 1 extra share";
        }

        // STATUS: Verified
        // https://vaas-stg.certora.com/output/11775/d794a47fa37c4c1e9f9fcb45f33ec6c5/?anonymousKey=8a280f8c9ba94d2c0ce98a7240969c02828ad17b
        ///@title mint function check for lower bound of shares minted
        ///@notice This rules checks that the mint function, for index > RAY, mints atleast the amount of shares specified by the caller
        rule mintCheckIndexGRayLowerBound(env e){
            uint256 shares;
            address receiver;
            uint256 assets;
            require getStaticATokenUnderlying() == ATok._underlyingAsset();
            require e.msg.sender != currentContract;
            uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

            uint256 receiverBalBefore = balanceOf(receiver);
            require receiverBalBefore + shares <= max_uint256;//avoiding overflow
            require index > RAY();
            
            assets = mint(e, shares, receiver);
            
            uint256 receiverBalAfter = balanceOf(receiver);
            // lowerbound
            assert receiverBalAfter >= receiverBalBefore + shares,"receiver should get no less than the amount of shares requested";
        }

        // STATUS: Verified
        // https://vaas-stg.certora.com/output/11775/bdf1ff3daa8542ebaac08c1950fdb89e/?anonymousKey=c5b77c1b715310da8f355d2b27bdb4008e70d519
        ///@title mint function check for index == RAY
        ///@notice This rule checks that, for index == RAY, the mind function will mint atleast the specifed amount of shares and upto 1 extra share over the specified amount
        rule mintCheckIndexEqualsRay(env e){
            uint256 shares;
            address receiver;
            uint256 assets;
            require getStaticATokenUnderlying() == ATok._underlyingAsset();
            require e.msg.sender != currentContract;
            uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

            uint256 receiverBalBefore = balanceOf(receiver);
            require receiverBalBefore + shares <= max_uint256;//avoiding overflow
            require index == RAY();
            
            assets = mint(e, shares, receiver);
            
            uint256 receiverBalAfter = balanceOf(receiver);
            
            assert receiverBalAfter <= receiverBalBefore + shares + 1,"receiver should get no more than the 1 extra share";
            assert receiverBalAfter >= receiverBalBefore + shares,"receiver should get no less than the amount of shares requested";
        }
