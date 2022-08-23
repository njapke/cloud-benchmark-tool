package main

import (
	computepb "google.golang.org/genproto/googleapis/cloud/compute/v1"
)

// TODO startup script
func generateNewInstance(name string, orchestratorName string) *computepb.Instance {
	newInstance := computepb.Instance{
		CanIpForward: FalsePointer(),
		Disks: []*computepb.AttachedDisk{
			{
				AutoDelete: TruePointer(),
				Boot:       TruePointer(),
				DeviceName: StringPointer(name),
				InitializeParams: &computepb.AttachedDiskInitializeParams{
					DiskSizeGb:  Int64Pointer(10),
					DiskType:    StringPointer("projects/masterarbeit-353409/zones/europe-west3-c/diskTypes/pd-balanced"),
					SourceImage: StringPointer("projects/masterarbeit-353409/global/images/arch-benchmark-base"),
				},
				Mode: StringPointer("READ_WRITE"),
				Type: StringPointer("PERSISTENT"),
			},
		},
		NetworkInterfaces: []*computepb.NetworkInterface{
			{
				AccessConfigs: []*computepb.AccessConfig{
					{
						Name:        StringPointer("External NAT"),
						NetworkTier: StringPointer("Premium"),
					},
				},
				StackType:  StringPointer("IPV4_ONLY"),
				Subnetwork: StringPointer("projects/masterarbeit-353409/regions/europe-west3/subnetworks/default"),
			},
		},
		MachineType: StringPointer("projects/masterarbeit-353409/zones/europe-west3-c/machineTypes/n2-standard-2"),
		Metadata: &computepb.Metadata{
			Items: []*computepb.Items{
				{
					Key:   StringPointer("startup-script-url"),
					Value: StringPointer("https://storage.googleapis.com/instance-runner-startup-script/" + orchestratorName + "/startup.sh"),
				},
			},
		},
		Name: StringPointer(name),
		Zone: StringPointer("projects/masterarbeit-353409/zones/europe-west3-c"),
	}
	return &newInstance
}

func FalsePointer() *bool {
	a := false
	return &a
}

func TruePointer() *bool {
	a := true
	return &a
}

func StringPointer(v string) *string {
	return &v
}

func Int64Pointer(i int64) *int64 {
	return &i
}