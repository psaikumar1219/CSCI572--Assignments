import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.StringTokenizer;


public class WordCount {

  public static class Map extends Mapper<Object, Text, Text, Text> {

      private final Text word = new Text();
      private final Text dId = new Text();

      @Override
      public void map(Object key, Text value, Context context){
          String[] split = value.toString().split("\\t", 2);
          System.out.println("--------------------");
          System.out.println(split[0]);
          System.out.println("--------------------");
          dId.set(split[0]);
          String document = split[1].replaceAll("[^a-zA-Z]+", " ").toLowerCase(Locale.ROOT);
          StringTokenizer tokenizer = new StringTokenizer(document, " ");
          while (tokenizer.hasMoreTokens()) {
              String token = tokenizer.nextToken();
              if (!token.trim().isEmpty()) {
                  word.set(token);
                  context.write(word, dId);
              }
          }
      }
  }

  public static class Reduce extends Reducer<Text, Text, Text, Text> {

      @Override
      public void reduce(Text word, Iterable<Text> dIds, Context context){
          Map<String, Integer> dIdToWFMap = new HashMap<>();
          for (Text dId : dIds) {
              String dIdString = dId.toString();
              dIdToWFMap.put(dIdString, dIdToWFMap.getOrDefault(dIdString, 0) + 1);
          }

          StringBuilder dIdWFs = new StringBuilder();
          for (Map.Entry<String, Integer> e : dIdToWFMap.entrySet()) {
              if (dIdWFs.length() > 0) {
                  dIdWFs.append("\t");
              }
              String dId = e.getKey();
              Integer WF = e.getValue();
              String dIdWF = String.format("%s:%d", dId, WF);
              System.out.println("--------------------");
              System.out.println(dIdWF);
              System.out.println("--------------------");
              dIdWFs.append(dIdWF);
          }

          context.write(word, new Text(dIdWFs.toString()));
      }
  }

  public static void main(String[] args){
      String if = args[0];
      String of = args[1];

      System.out.println("--------------------");
      System.out.println(if);
      System.out.println("--------------------");
      System.out.println(of);
      System.out.println("--------------------");

      Configuration configuration = new Configuration();
      Job j = Job.getInstance(configuration, "Inverted Index");
      j.setJarByClass(WordCount.class);
      j.setMapperClass(Map.class);
      j.setReducerClass(Reduce.class);
      j.setOutputKeyClass(Text.class);
      j.setOutputValueClass(Text.class);

      Path ifp = new Path(if);
      Path ofp = new Path(of);
      System.out.println("--------------------");
      System.out.println(ifp);
      System.out.println("--------------------");
      System.out.println(ofp);
      System.out.println("--------------------");
      FileSystem fs = ofp.getFileSystem(configuration);
      if (fs.exists(ofp)) {
          fs.delete(ofp, true);
      }
      FileInputFormat.addInputPath(j, ifp);
      FileOutputFormat.setOutputPath(j, ofp);

      System.exit(j.waitForCompletion(true) ? 0 : 1);
  }
}// WordCount

