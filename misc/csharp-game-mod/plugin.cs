using System;
using System.Collections.Generic;
using System.Reflection;
using BepInEx;
using BepInEx.Configuration;

namespace CosmeticTokenAdder
{
    [BepInPlugin(
        "mugenq.cosmetictokenadder",
        "Cosmetic Token Adder",
        "1.0.1"
    )]
    public sealed class Plugin : BaseUnityPlugin
    {
        private ConfigEntry<int> _amountToAdd;
        private ConfigEntry<string> _tokenRarity;
        private ConfigEntry<bool> _addTokens;

        private bool _waitingToAdd;

        private static readonly FieldInfo SaveReadyField =
            typeof(MetaManager).GetField(
                "saveReady",
                BindingFlags.Instance |
                BindingFlags.Public |
                BindingFlags.NonPublic
            );

        private static readonly FieldInfo CosmeticTokensField =
            typeof(MetaManager).GetField(
                "cosmeticTokens",
                BindingFlags.Instance |
                BindingFlags.Public |
                BindingFlags.NonPublic
            );

        private static readonly string[] RarityNames =
        {
            "Common",
            "Uncommon",
            "Rare",
            "UltraRare"
        };

        private void Awake()
        {
            _amountToAdd = Config.Bind(
                "Token Adder",
                "Amount To Add",
                10,
                new ConfigDescription(
                    "Number of cosmetic tokens to add.",
                    new AcceptableValueRange<int>(1, 1000)
                )
            );

            _tokenRarity = Config.Bind(
                "Token Adder",
                "Token Rarity",
                "UltraRare",
                new ConfigDescription(
                    "Rarity of cosmetic token to add.",
                    new AcceptableValueList<string>(
                        RarityNames
                    )
                )
            );

            _addTokens = Config.Bind(
                "Token Adder",
                "Add Tokens",
                false,
                "Turn this ON to add the configured number " +
                "of cosmetic tokens. Resets to OFF automatically."
            );

            _addTokens.SettingChanged += OnAddTokensChanged;

            Logger.LogInfo(
                "Cosmetic Token Adder loaded."
            );

            if (SaveReadyField == null)
            {
                Logger.LogError(
                    "Could not find MetaManager.saveReady."
                );
            }

            if (CosmeticTokensField == null)
            {
                Logger.LogError(
                    "Could not find MetaManager.cosmeticTokens."
                );
            }
        }

        private void OnAddTokensChanged(
            object sender,
            EventArgs args)
        {
            if (!_addTokens.Value)
                return;

            _waitingToAdd = true;

            Logger.LogInfo(
                "Token addition requested."
            );
        }

        private void Update()
        {
            if (!_waitingToAdd)
                return;

            MetaManager manager = MetaManager.instance;

            if (manager == null)
                return;

            if (SaveReadyField == null)
            {
                CancelRequest(
                    "saveReady field is unavailable."
                );

                return;
            }

            bool saveReady =
                (bool)SaveReadyField.GetValue(manager);

            if (!saveReady)
                return;

            AddConfiguredTokens(manager);
        }

        private void AddConfiguredTokens(
            MetaManager manager)
        {
            _waitingToAdd = false;

            SemiFunc.Rarity rarity =
                ParseRarity(_tokenRarity.Value);

            int amount = _amountToAdd.Value;

            try
            {
                int beforeCount =
                    GetTokenCount(manager);

                for (int i = 0; i < amount; i++)
                {
                    manager.CosmeticTokenAdd(rarity);
                }

                int afterCount =
                    GetTokenCount(manager);

                Logger.LogInfo(
                    $"Added {amount} {rarity} cosmetic tokens."
                );

                Logger.LogInfo(
                    $"Token list count: " +
                    $"{beforeCount} -> {afterCount}"
                );
            }
            catch (Exception exception)
            {
                Logger.LogError(
                    "Failed to add cosmetic tokens: " +
                    exception
                );
            }
            finally
            {
                ResetToggle();
            }
        }

        private int GetTokenCount(
            MetaManager manager)
        {
            if (CosmeticTokensField == null)
                return -1;

            object value =
                CosmeticTokensField.GetValue(manager);

            List<int> tokens =
                value as List<int>;

            if (tokens == null)
                return -1;

            return tokens.Count;
        }

        private SemiFunc.Rarity ParseRarity(
            string value)
        {
            if (Enum.TryParse(
                value,
                true,
                out SemiFunc.Rarity rarity))
            {
                return rarity;
            }

            Logger.LogWarning(
                $"Invalid rarity '{value}'. " +
                "Falling back to UltraRare."
            );

            return SemiFunc.Rarity.UltraRare;
        }

        private void CancelRequest(
            string reason)
        {
            _waitingToAdd = false;

            Logger.LogError(
                "Token addition cancelled: " +
                reason
            );

            ResetToggle();
        }

        private void ResetToggle()
        {
            _addTokens.Value = false;
            Config.Save();
        }
    }
}