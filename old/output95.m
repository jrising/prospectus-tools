function output95(filename, xx, means, min95s, max95s)

fp = fopen(filename, 'w');
fprintf(fp, 'dpc1,mean,.025,.975\n');
fclose(fp);

if size(xx, 1) == 1
  xx = xx';
end
if size(means, 1) == 1
  means = means';
end
if size(min95s, 1) == 1
  min95s = min95s';
end
if size(max95s, 1) == 1
  max95s = max95s';
end

dlmwrite(filename, [xx means min95s max95s], '-append');