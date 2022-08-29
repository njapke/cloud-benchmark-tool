package main

import (
	compute "cloud.google.com/go/compute/apiv1"
	"cloud.google.com/go/storage"
	"context"
	log "github.com/sirupsen/logrus"
	"google.golang.org/api/iterator"
	computepb "google.golang.org/genproto/googleapis/cloud/compute/v1"
)

func uploadBytes(toUpload []byte, orchestratorName string, gcpProjectName string, gcpBucketName string, gclient *storage.Client, ctx context.Context) {
	wc := gclient.Bucket(gcpBucketName).Object(orchestratorName + "/startup.sh").NewWriter(ctx)
	wc.ContentType = "text/plain"
	wc.Metadata = map[string]string{
		"x-goog-project-id": gcpProjectName,
	}

	log.Debugln("Uploading data to bucket")
	i, err := wc.Write(toUpload)
	if err != nil {
		log.Fatalln(err)
	}
	err = wc.Close()
	if err != nil {
		log.Fatalln(err)
	}
	log.Debugf("Wrote %d\n", i)
	log.Debugln("Finished uploading data to bucket")
}

func createInstance(name string, orchestratorName string, gcpProjectName string, gcpBucketName string, gcpImageName string, gclient *compute.InstancesClient, ctx context.Context) {
	log.Debugln("Creating instance " + name)
	instance := generateNewInstance(name, orchestratorName, gcpProjectName, gcpBucketName, gcpImageName)

	req := computepb.InsertInstanceRequest{
		InstanceResource: instance,
		Project:          gcpProjectName,
		Zone:             "europe-west3-c",
	}

	op, err := gclient.Insert(ctx, &req)
	if err != nil {
		log.Fatalln(err)
	}

	err = op.Wait(ctx)
	if err != nil {
		log.Fatalln(err)
	}
	log.Debugln("Finished creating instance " + name)
}

func shutdownAllInstances(toShutdown *[]string, gcpProjectName string, gclient *compute.InstancesClient, ctx context.Context) {
	log.Debugln("Removing all instances")
	listReq := computepb.ListInstancesRequest{
		Project: gcpProjectName,
		Zone:    "europe-west3-c",
	}

	it := gclient.List(ctx, &listReq)

	for {
		instance, err := it.Next()
		if err == iterator.Done {
			log.Debugln(err)
			break
		} else if err != nil {
			log.Fatalln(err)
		}

		// Only shut down instances in list
		if contains(*instance.Name, toShutdown) {
			log.Debugln("Removing instance " + *instance.Name)
			delReq := computepb.DeleteInstanceRequest{
				Instance: *instance.Name,
				Project:  gcpProjectName,
				Zone:     "europe-west3-c",
			}
			op, err := gclient.Delete(ctx, &delReq)
			if err != nil {
				log.Fatalln(err)
			}

			err = op.Wait(ctx)
			if err != nil {
				log.Fatalln(err)
			}
			log.Debugln("Finished removing instance " + *instance.Name)
		}
	}
	log.Debugln("Finished removing all instances")
}

func contains(elem string, list *[]string) bool {
	for i := 0; i < len(*list); i++ {
		if elem == (*list)[i] {
			return true
		}
	}
	return false
}
