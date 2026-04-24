// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class ThirdPerson : ModuleRules
{
	public ThirdPerson(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"ThirdPerson",
			"ThirdPerson/Variant_Platforming",
			"ThirdPerson/Variant_Platforming/Animation",
			"ThirdPerson/Variant_Combat",
			"ThirdPerson/Variant_Combat/AI",
			"ThirdPerson/Variant_Combat/Animation",
			"ThirdPerson/Variant_Combat/Gameplay",
			"ThirdPerson/Variant_Combat/Interfaces",
			"ThirdPerson/Variant_Combat/UI",
			"ThirdPerson/Variant_SideScrolling",
			"ThirdPerson/Variant_SideScrolling/AI",
			"ThirdPerson/Variant_SideScrolling/Gameplay",
			"ThirdPerson/Variant_SideScrolling/Interfaces",
			"ThirdPerson/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
