#docker build --no-cache --rm -t shawndp/ppip:1.0 .  1>std.log 2>err.log
docker build --rm -t shawndp/ppip:1.0 .  1>std.log 2>err.log
