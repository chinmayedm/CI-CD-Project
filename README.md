# AWS VPC Architecture with Public Subnets and EC2

This README explains **each AWS service** used in the given architecture diagram and provides a **step-by-step guide** to build it from scratch. The setup demonstrates how an EC2 instance inside a **public subnet** connects securely to the **Internet** using AWS networking components.

---

## 📌 Architecture Overview

![AWS VPC Public Subnet EC2 Architecture]()

The architecture consists of:

* A custom **VPC**
* Two **Public Subnets**
* An **Internet Gateway (IGW)**
* A **Route Table**
* An **EC2 Instance**
* **Security Groups**
* **Key Pair** for SSH access

This setup allows an EC2 instance to:

* Get a public IP
* Communicate with the internet
* Be accessed securely via SSH

---

## 🧩 AWS Services Explained

### 1️⃣ VPC (Virtual Private Cloud)

* Acts as an isolated virtual network in AWS.
* CIDR Block: `10.0.0.0/16`
* All subnets, route tables, and gateways exist inside the VPC.

---

### 2️⃣ Subnets

#### Public Subnet 1

* CIDR: `10.0.0.0/24`
* Used for public-facing resources

#### Public Subnet 2

* CIDR: `10.0.1.0/24`
* Hosts the EC2 instance

📌 A subnet is called **public** only if it has a route to the Internet Gateway.

---

### 3️⃣ Internet Gateway (IGW)

* Enables communication between VPC and the Internet.
* Attached directly to the VPC.
* Required for public subnets.

---

### 4️⃣ Route Table

* Controls how traffic is routed.
* Contains routes such as:

```
Destination    Target
0.0.0.0/0      Internet Gateway (IGW)
```

* Associated with public subnets.

---

### 5️⃣ EC2 Instance

* A virtual server running inside the public subnet.
* Assigned:

  * Public IP
  * Private IP
* Used to host applications or services.

---

### 6️⃣ Security Group (Inbound & Outbound Access)

* Acts as a **stateful virtual firewall** for the EC2 instance.
* Controls **who can access** the instance and **on which ports**.

#### 🔐 Inbound Rules (VERY IMPORTANT)

Inbound rules define traffic **allowed INTO** the EC2 instance.

| Type  | Protocol | Port | Source   | Purpose                      |
| ----- | -------- | ---- | -------- | ---------------------------- |
| SSH   | TCP      | 22   | My IP    | Secure remote login          |
| HTTP  | TCP      | 80   | Anywhere | Web access (optional)        |
| HTTPS | TCP      | 443  | Anywhere | Secure web access (optional) |

📌 **Best Practice**:

* Never allow SSH from `0.0.0.0/0`
* Always restrict SSH to **My IP**

#### 🔄 Outbound Rules

* Allow **all traffic** (`0.0.0.0/0`)
* Required for software updates and internet access

---

### 7️⃣ SSH Access (Secure Login)

SSH allows you to securely connect to the EC2 instance using a **key pair** instead of passwords.

#### 🔑 Key Pair Concept

* **Private Key (.pem)** → Stored securely on your system
* **Public Key** → Stored automatically in AWS

AWS uses **public-key cryptography** to authenticate users.

#### 🔐 SSH Connection Steps

```bash
# Move key to safe location
mv mykey.pem ~/.ssh/

# Set correct permissions
chmod 400 ~/.ssh/mykey.pem

# Connect to EC2
ssh -i ~/.ssh/mykey.pem ec2-user@<EC2-Public-IP>
```

📌 If connection fails, check:

* Security Group inbound rule (SSH allowed?)
* Correct username (`ec2-user` for Amazon Linux)
* Public IP assigned to EC2

---

### 7️⃣ Key Pair

* Used for secure SSH login.
* Consists of:

  * **Private Key** (stored locally)
  * **Public Key** (stored in AWS)

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Create VPC

1. Go to **VPC Dashboard → Create VPC**
2. Name: `MyVPC`
3. CIDR: `10.0.0.0/16`

---

### Step 2: Create Subnets

#### Subnet 1

* Name: `Public-Subnet-1`
* CIDR: `10.0.0.0/24`

#### Subnet 2

* Name: `Public-Subnet-2`
* CIDR: `10.0.1.0/24`

---

### Step 3: Create and Attach Internet Gateway

1. VPC → Internet Gateways → Create IGW
2. Attach it to `MyVPC`

---

### Step 4: Create Route Table

1. VPC → Route Tables → Create
2. Add route:

```
0.0.0.0/0 → Internet Gateway
```

3. Associate route table with both public subnets

---

### Step 5: Enable Auto-Assign Public IP

* Select each public subnet
* Enable **Auto-assign IPv4 Public IP**

---

### Step 6: Create Security Group

Inbound Rules:

* SSH (22) → My IP
* HTTP (80) → Anywhere (optional)

Outbound Rules:

* Allow all

---

### Step 7: Create Key Pair

1. EC2 → Key Pairs → Create
2. Type: RSA
3. Download `.pem` file

---

### Step 8: Launch EC2 Instance

1. EC2 → Launch Instance
2. Choose Amazon Linux
3. Select `Public-Subnet-2`
4. Enable public IP
5. Attach security group
6. Select key pair

---

### Step 9: Connect to EC2

```bash
chmod 400 mykey.pem
ssh -i mykey.pem ec2-user@<Public-IP>
```

---

## ✅ Final Outcome

* EC2 instance is publicly accessible
* Internet connectivity is enabled
* Secure access via SSH
* Architecture matches AWS best practices

---

## 🎯 Use Cases

* Web server hosting
* Learning AWS networking
* Cloud & DevOps practice
* Interview & certification preparation

---

## 🏁 Conclusion

This architecture demonstrates the foundational AWS networking concepts including **VPC, subnets, routing, gateways, and security**. Understanding this setup is critical for roles in **Cloud, DevOps, and Solutions Architecture**.

---
