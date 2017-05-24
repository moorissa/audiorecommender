# Graph Analysis using SQL and GraphX

#### Due on 7th April 11:59pm EST.

In this assignment, you will import a graph (stored as text files) into SQL and GraphX and answer some questions based on it. 

### A. Get the data
Run the VM provided in the Hadoop assignment and clone this repo:
```
$ git clone https://github.com/kartikeya1994/graph-analysis.git
```
`data.zip` contains two files: amazon-data.txt and amazon-meta-clean.txt. The graph is a representation of Amazon website’s “Customers Who Bought This Item Also Bought” feature. If purchase of product i  frequently leads to purchase of product j, then the graph contains a directed edge from i to j. The data was collected in 2003 by crawling the Amazon website, and contains product metadata and review information about 548,552 different products (Books, music CDs, DVDs and VHS video tapes). More info is available here: 
1.	`amazon-data.txt`: each line has two vertex ids `i` and `j` representing an edge  `i -> j`.  [More info](https://snap.stanford.edu/data/amazon0302.html).
2.	`amazon-meta-clean.txt`: each line contains the following info: `vertex_id \t title \t type \t salesrank`. [More info](https://snap.stanford.edu/data/amazon-meta.html).

Switch to repo directory:
```
$ cd graph-analysis
```

To extract the files through console:
```
[graph-analysis]$ unzip data.zip
```

### B. Install MySQL and load data into tables
Run the following to install `mysql-server`. Press `y` or `yes` on all the prompts. 
```
$ sudo yum install mysql-server
```
Start the sql server:
```
$ sudo /sbin/service mysqld start
```
And ensure that there’s a green OK indicating that `mysqld` has started.

Configure `mysqld`:
```
$ sudo /usr/bin/mysql_secure_installation
```
Default password is blank. Hit `no` for all prompts except `reload privilege tables`, hit `yes` for that. 

Start the mysql shell:
```
$ /usr/bin/mysql -u root
```
Create a new database callled `amazon`:
```
mysql> CREATE DATABASE amazon;
```
Since the assignment may be autochecked, make sure your database and tables have the same name as given here. 
Select the database you just created:
```
mysql> USE amazon;
```
Create a table to store the edges of the graph:
```
mysql> CREATE TABLE links(
     > from_item INT,
     > to_item INT
     > );
```
Load data onto the table:
```
mysql> LOAD DATA LOCAL INFILE ‘/home/training/graph-analysis/amazon-data.txt’ INTO TABLE links;
```

Similarly, create another table named `metadata` for the vertex metadata and load `amazon-meta-clean.txt` into it. 
```
mysql> CREATE TABLE metadata(
     > id INT,
     > title VARCHAR(200),
     > type VARCHAR(200),
     > salesrank INT,
     > PRIMARY KEY (id)
     > );
```

Install the MySQL Python driver:
```
$ sudo yum -y install MySQL-python
```

#### C. Answer questions using SQL
Write queries to answer the following questions. Take a look at `uni1234.py` that has been provided to you, it has sample Python code for connecting to SQL, and space to write your answers. Make sure you rename the file with your UNI. 
1.	The name of the most co-purchased product (if `i -> j` is the edge, then `j` is the co-purchased product here).
2.	The name of the most co-purchased DVD. 
3.	The average number of products that a product is co-purchased with. This is essentially the average in-degree of the given graph. 
4.	Count of all triplets of products containing the book `The Maine Coon Cat (Learning About Cats)`  that could form a ‘combo’ (say, for the purpose of a discount), such that the products in the triplet are co-purchased.  More specifically, if `a`, `b`, `c` form a triplet, then `a -> b`, `b->c`, `c->a` is true, and one of `a`, `b`, `c` needs to be the cat book specified above. 
5.	Find the length of the shortest path between the `Video` titled `Star Wars Animated Classics - Droids` (as source node) and the `Book` titled `The Maine Coon Cat (Learning About Cats)` (as destination node).

### D. Get Spark running
GraphX is a part of Spark. You will need to download and setup another VM for this. If you have a pre-existing `Spark` installation or wish to do this another way, you're free to do so. 

Install [Vagrant](https://www.vagrantup.com/downloads.html) on your host machine. You should already have [Virtualbox](https://www.virtualbox.org/wiki/Downloads) installed from the Hadoop assignment.

For this you'll need to clone the repo again on the host machine. Open the console and navigate to the git repo. Notice `Vagrantfile`, this contains the configuration of the VM. Run the following to get the VM running:
```
vagrant up
```
Vagrant will download the VM when you run this for the first time. Give it a few minutes. When done, `SSH` into the VM using Vagrant:
 ```
 vagrant ssh
 ``` 
If you're on Windows, this command will only print the host, port and location of private key. You need to do two things to be able to `SSH`:
1. Download and install [PuTTYgen](https://winscp.net/eng/docs/ui_puttygen#obtaining_and_starting_puttygen). Load your `private_key` in PuTTYgen and generate a PuTTY compatible key (`.ppk` file).
2. Download and install [PuTTY](http://www.putty.org/). In `Connection -> SSH -> Auth`, specify the path to your private key. Specify the host and port in `Session` and hit `Open`.

List directories in the repo folder: 
```
vagrant@sparkvm/graph-analysis:~$  ls
```
You should notice a folder called `vagrant` (create one if not present). This is synced with the folder `vagrant` in the same directory as the `Vagrantfile` on your host machine. Put your data in this folder to be able to access it on the VM. 

If you need to shut the VM, type `exit` on the console to close the SSH session and run `vagrant halt` on the host machine (in the same directory as your `Vagantfile`).

### E. Using Spark's GraphX
Start `Spark` in the same directory as your unzipped data files:
```
vagrant@sparkvm:~/graph-analysis$  spark-shell
```
You should get Spark's Scala REPL that looks like this:
```
scala>
```
Write `Spark` commands to answer the following. Paste the Spark commands you wrote into graphx.txt

1.	The name of the most co-purchased product (if `i -> j` is the edge, then `j` is the co-purchased product here).
2.	The average number of products that a product is co-purchased with. This is essentially the average in-degree of the given graph. 
3.	Find the length of the shortest path between the `Video` titled `Star Wars Animated Classics - Droids` and the `Book` titled `The Maine Coon Cat (Learning About Cats)`.
4. Count of all unique triangles in graph. (Permutations of order of vertices are considered to be the same triangle). Record this as `ans6` in `uni1234.py`. 

The solution to part 1 is provided below as an example. 

Import the necessary libraries:
```
import org.apache.spark._
import org.apache.spark.graphx._
```

Create an RDD for the vertices:
```
val v = sc.textFile("amazon-meta-clean.txt").map(x => (x.split("\t")(0).toLong,(x.split("\t")(1),x.split("\t")(2))) )
```
Create an RDD for the edges:
```
val e = sc.textFile("amazon-data.txt").map(x => Edge(x.split("\t")(0).toLong,x.split("\t")(1).toLong,0L))
```
Create the graph:
```
val g = Graph(v,e)
```
The graph object has several useful data members, the `in-degree` for each node is relevant for this part. Get the max `in-degree` as follows:
```
val ansNode = g.inDegrees.reduce((a,b)=> if (a._2 > b._2) a else b)
```
You are encouraged to skim through the [GraphX Documentation](http://spark.apache.org/docs/latest/graphx-programming-guide.html) to learn more about `Graph` data members and functions.  
Looking-up the title of the node with the max in-degree should be your answer:
```
v.lookup(ansNode._1)
```

#### Submitting
On completion, submit a `.zip` containing `uni1234.py` and `uni1234.txt` on CourseWorks, both renamed to your UNI. Due on 7th April 11:59pm EST. Example of a submission:
```
kuu2101.zip
|--kuu2101.py
|--kuu2101.txt
```
# Building Spotify's 'Weekly Discover' with Spark
