11/11/2026

# What did I do?

Pushed Journal API image to Azure container registry

# What worked?

The following commands were used to complete the process.

`az acr login --name` was used to authenticate Docker with ACR.

`docker push` was used to push the image to the ACR.

`docker run` pulls and runs the image from the ACR.

`az acr repository list -n crjournalprodnewzealandnorth001 --output table` lists the repository the image is under.

`az acr repository show-tags -n crjournalprodnewzealandnorth001 --repository journal-api --output table` shows the tag of the image.

# What I struggled with, and how did I solve it?

Initially, when running `docker push` I got this error message.

```
push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

First thing I did was run the command `az acr login` to verify if Docker has authenticated with ACR. This was not the issue as I got `Login succeeded` message. The next thing I checked was the permissions. It turned out ACR splits its permission model into a control plane and data plane. The control plane focuses on managing the registry itself, while the data plane focuses on pushing images to and pulling images from the repository. Even if I am the Owner of registry I still need the Container Registry Repository Writer and Container Registry Repository Catalog Lister roles to push and pull from ACR. I assigned to roles to myself and ran the run command again and everything worked.