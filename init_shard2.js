rs.initiate(
    {
        _id : "shard2",
        members: [
            { _id : 0, host : "114.212.84.175:28010" ,priority : 2 },
            { _id : 1, host : "114.212.84.175:28011" ,priority : 1 },
            { _id : 2, host : "114.212.84.175:28012" ,arbiterOnly :true }
        ]
    }
)
rs.status();