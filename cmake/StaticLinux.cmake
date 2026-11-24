# Apply after project() initializes the platform's default library suffixes.
# This also makes transitive dependencies in CURLConfig.cmake select archives.
set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
