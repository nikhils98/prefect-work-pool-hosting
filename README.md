[Accompanying guide](https://nikhils98.github.io/posts/self-host-prefect-with-ecs-work-pool)

# Project structure

The root contains the code for the flow inside `main.py`.

The `infrastructure` directory houses the Pulumi project.

Both projects are independent; have their own `requirements.txt` and the packages should be installed in their own venvs.

## Infrastructure

If you're new to Pulumi, check out the official guide to [get started](https://www.pulumi.com/docs/clouds/aws/get-started/). When you bootstrap a new project, it'll come with a `.gitignore` file which I have removed since we're tracking the project in git in the root directory.

Pulumi manages different environments via a concept called [stack](https://www.pulumi.com/docs/concepts/stack/). Each stack has a name and config file for e.g I created one named `dev` in order to test the project. Hence we have the file `Pulumi.dev.yaml`. Apart from the region where you want to deploy this stack at and `encryptionsalt` which is generated automatically, there are a few custom variables, the details for which can be found in the config file itself. Notice that each of those variables is prefixed with the project name. A variable can be a simple value, object or an array.

Running the project shouldn't take more than a couple minutes. But it's worth noting however that EC2 instance may take a few more minutes to initialize and get registered in the ECS cluster. When that's done, the server and worker containers will be up and running as well.